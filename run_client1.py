from models import Client


def run():
    client = Client(server_path='127.0.0.1:3000', name='Player1')
    client.run()


if __name__ == '__main__':
    run()

