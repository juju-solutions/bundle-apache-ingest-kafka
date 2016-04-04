# Big Data Ingestion with Apache Kafka

This bundle is an 11 node cluster designed to scale out. Built around Apache
Hadoop components, it contains the following units:

  * 1 NameNode (HDFS)
  * 1 ResourceManager (YARN)
  * 3 Slaves (DataNode and NodeManager)
  * 1 Flume-HDFS
    - 1 Plugin (colocated on the Flume unit)
  * 1 Flume-Kafka
  * 1 Kafka
  * 3 Zookeepers

The Flume-HDFS unit provides an Apache Flume agent featuring an Avro source,
memory channel, and HDFS sink. This agent supports a relation with the
Flume-Kafka charm (`apache-flume-kafka`) to ingest messages published to a
given Kafka topic into HDFS.


## Usage

Deploy this bundle using juju-quickstart:

    juju quickstart apache-ingest-kafka

See `juju quickstart --help` for deployment options, including machine
constraints and how to deploy a locally modified version of the
`apache-ingestion-flume` bundle.yaml.


## Configuration

The default Kafka topic where messages are published is unset. Set this to
an existing Kafka topic as follows:

    juju set flume-kafka kafka_topic='<topic_name>'

If you don't have a Kafka topic, you may create one (and verify successful
creation) with:

    juju action do kafka/0 create-topic topic=<topic_name> \
     partitions=1 replication=1
    juju action fetch <id>  # <-- id from above command

Once the Flume agents start, messages will start flowing into
HDFS in year-month-day directories here: `/user/flume/flume-kafka/%y-%m-%d`.


## Status and Smoke Test

The services provide extended status reporting to indicate when they are ready:

    juju status --format=tabular

This is particularly useful when combined with `watch` to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The charm for each core component (namenode, resourcemanager)
also each provide a `smoke-test` action that can be used to verify that each
component is functioning as expected.  You can run them all and then watch the
action status list:

    juju action do namenode/0 smoke-test
    juju action do resourcemanager/0 smoke-test
    watch -n 0.5 juju action status

Eventually, all of the actions should settle to `status: completed`.  If
any go instead to `status: failed` then it means that component is not working
as expected.  You can get more information about that component's smoke test:

    juju action fetch <action-id>

### Smoke test Flume
SSH to the Flume unit and verify the flume-ng java process is running:

    juju ssh flume-hdfs/0
    ps -ef | grep flume  # verify process is running
    exit

### Test Kafka-Flume
Generate Kafka messages on the `flume-kafka` unit with the producer script:

    juju ssh flume-kafka/0
    kafka-console-producer.sh --broker-list localhost:9092 --topic <topic_name>
    <type message, press Enter>

To verify these messages are being stored into HDFS, SSH to the `flume-hdfs`
unit, locate an event, and cat it:

    juju ssh flume-hdfs/0
    hdfs dfs -ls /user/flume/flume-kafka  # <-- find a date
    hdfs dfs -ls /user/flume/flume-kafka/yyyy-mm-dd  # <-- find an event
    hdfs dfs -cat /user/flume/flume-kafka/yyyy-mm-dd/FlumeData.[id]


## Scale Out Usage

This bundle was designed to scale out. To increase the amount of Compute
Slaves, you can add units to the compute-slave service. To add one unit:

    juju add-unit compute-slave

You can also add multiple units, for examle, to add four more compute slaves:

    juju add-unit -n4 compute-slave


## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
