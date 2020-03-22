from models import Server


def run():
    server = Server(server_path='127.0.0.1:3000')
    server.run()


if __name__ == '__main__':
    run()

