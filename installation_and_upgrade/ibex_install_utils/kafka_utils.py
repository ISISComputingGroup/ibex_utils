from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

REQUIRED_SUFFIXES = ["_events", "_sampleEnv", "_runInfo", "_epicsForwarderConfig", "_detSpecMap"]


def get_existing_topics(kafka_broker):
    return KafkaConsumer(bootstrap_servers=[kafka_broker]).topics()


def add_required_topics(kafka_broker, instrument):
    """
    Adds required Kafka topics for the instrument

    Args:
        kafka_broker: the broker to add the topics to
        instrument: the name of the instrument for which to add the topics
    """
    required_topics = set(instrument + suffix for suffix in REQUIRED_SUFFIXES)
    existing_topics = set(
        filter(lambda topic: topic.startswith(instrument), get_existing_topics(kafka_broker))
    )

    if required_topics != existing_topics:
        topic_names_to_add = required_topics - existing_topics

        topic_list = [
            NewTopic(name=name, num_partitions=1, replication_factor=3)
            for name in topic_names_to_add
        ]

        admin_client = KafkaAdminClient(bootstrap_servers=kafka_broker, client_id="install_script")
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
