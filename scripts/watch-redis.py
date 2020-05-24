from workers.config import config
import json
import redis


def main():
    redis_cfg = config['creds']['redis']
    rs = redis.Redis(host=redis_cfg['host'], password=redis_cfg['password'], port=redis_cfg['port'])
    pubsub = rs.pubsub()
    with pubsub:
        pubsub.subscribe('*')
        for item in pubsub.listen():
            try:
                evt = json.loads(item['data'])
            except:
                continue
            print(evt)


if __name__ == '__main__':
    main()