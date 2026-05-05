import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, DataTypes, StreamTableEnvironment
from pyflink.table.expressions import lit, col
from pyflink.table.window import Session


def create_sessionized_events_sink_postgres(t_env):
    """Create sink table for sessionized events"""
    table_name = 'sessionized_events'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            session_start TIMESTAMP(3),
            session_end TIMESTAMP(3),
            ip VARCHAR,
            host VARCHAR,
            num_events BIGINT,
            PRIMARY KEY (session_start, ip, host) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = '{os.environ.get("POSTGRES_URL")}',
            'table-name' = '{table_name}',
            'username' = '{os.environ.get("POSTGRES_USER", "postgres")}',
            'password' = '{os.environ.get("POSTGRES_PASSWORD", "postgres")}',
            'driver' = 'org.postgresql.Driver'
        );
    """
    t_env.execute_sql(sink_ddl)
    return table_name


def create_processed_events_source_kafka(t_env):
    """Create Kafka source table for web events"""
    kafka_key = os.environ.get("KAFKA_WEB_TRAFFIC_KEY", "")
    kafka_secret = os.environ.get("KAFKA_WEB_TRAFFIC_SECRET", "")
    table_name = "web_events_kafka"
    pattern = "yyyy-MM-dd''T''HH:mm:ss.SSS''Z''"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            ip VARCHAR,
            event_time VARCHAR,
            referrer VARCHAR,
            host VARCHAR,
            url VARCHAR,
            geodata VARCHAR,
            window_timestamp AS TO_TIMESTAMP(event_time, '{pattern}'),
            WATERMARK FOR window_timestamp AS window_timestamp - INTERVAL '15' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = '{os.environ.get('KAFKA_URL')}',
            'topic' = '{os.environ.get('KAFKA_TOPIC')}',
            'properties.group.id' = '{os.environ.get('KAFKA_GROUP')}',
            'properties.security.protocol' = 'SASL_SSL',
            'properties.sasl.mechanism' = 'PLAIN',
            'properties.sasl.jaas.config' = 'org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain.PlainLoginModule required username=\"{kafka_key}\" password=\"{kafka_secret}\";',
            'scan.startup.mode' = 'latest-offset',
            'properties.auto.offset.reset' = 'latest',
            'format' = 'json'
        );
    """
    t_env.execute_sql(source_ddl)
    return table_name


def sessionization():
    """
    Main function to sessionize web events by IP and host with 5-minute session gap
    """
    print('Starting Sessionization Job!')
    
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10000)  # 10 seconds
    env.set_parallelism(3)

    # Set up the table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    try:
        # Create Kafka source table
        source_table = create_processed_events_source_kafka(t_env)
        print(f'Created Kafka source table: {source_table}')

        # Create PostgreSQL sink table
        sink_table = create_sessionized_events_sink_postgres(t_env)
        print(f'Created PostgreSQL sink table: {sink_table}')

        # Perform sessionization with 5-minute gap
        # Group by IP and host, count events in each session
        print('Executing sessionization query...')
        t_env.from_path(source_table) \
            .window(
                Session.with_gap(lit(5).minutes).on(col("window_timestamp")).alias("w")
            ) \
            .group_by(
                col("w"),
                col("ip"),
                col("host")
            ) \
            .select(
                col("w").start.alias("session_start"),
                col("w").end.alias("session_end"),
                col("ip"),
                col("host"),
                col("ip").count.alias("num_events")
            ) \
            .execute_insert(sink_table) \
            .wait()

        print('Sessionization job completed successfully!')

    except Exception as e:
        print(f"Sessionization job failed: {str(e)}")
        raise


if __name__ == '__main__':
    sessionization()
