import pika
from data_collector import *
import sys
import threading
from random import randint
from time import sleep
from tinydb import TinyDB

db_lock = threading.Lock()


def consume_urls_from_queue(num_threads_chosen):
    def callback(ch, method, properties, body):
        url = body.decode('utf-8')

        data = extract_product_details(url)
        if data is not None:
            with db_lock:
                db.insert(data)
            print(f"Processed URL: {url} (Thread: {threading.current_thread().name})")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consumer_thread():
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='url_queue')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='url_queue', on_message_callback=callback)

        print(f"Consumer is waiting for messages. To exit press CTRL+C (Thread: {threading.current_thread().name})")
        channel.start_consuming()

    num_threads = num_threads_chosen

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=start_consumer_thread, name=f"Thread-{i}")
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    name_file = sys.argv[1]
    num_threads = sys.argv[2]
    db = TinyDB(f'{name_file}.json')
    consume_urls_from_queue(int(num_threads))
