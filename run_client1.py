from models import Client


def run():
    client = Client(server_path='167.99.5.145:3000', name='Player1')
    client.run()


if __name__ == '__main__':
    run()

