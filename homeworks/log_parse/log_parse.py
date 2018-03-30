# -*- encoding: utf-8 -*-
import re
from datetime import datetime
from collections import Counter


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    with open('log.log', 'r') as log:
        reg_exp = r'^\[(?P<time>\d+/\w+/\d+\s\d+:\d+:\d+)]\s\"(?P<type>\w+)\s(?P<URL>[^\"]+)\"\s(?P<code>\d+)\s(?P<rtime>\d+)$'
        c = []
        slow_urls = {}

        for line in log.readlines():
            matches = re.match(reg_exp, line)

            if matches:
                date_url, type_url, url_info, code, r_time = matches.groups()
                url, version = url_info.split(' ')
                url = url.split('://')[1]
                date = datetime.strptime(date_url, '%d/%b/%Y %H:%M:%S')

                if slow_urls.get(url):
                    slow_urls[url]['time'] += int(r_time)
                    slow_urls[url]['count'] += 1
                else:
                    slow_urls[url] = {
                        'time': int(r_time),
                        'count': 1
                    }

                if ignore_www:
                    url = url.replace('www.', '')

                if start_at and date <= datetime.strptime(start_at, '%d.%m.%Y %H:%M'):
                    continue
                if stop_at and date >= datetime.strptime(stop_at, '%d.%m.%Y %H:%M'):
                    continue

                if url not in ignore_urls:
                    c.append(url)

                if ignore_files:
                    url_files = url.split('/')
                    if '.' in url_files[-1]:
                        c.remove(url)

                if request_type and request_type != type_url:
                    continue

    if slow_queries:
        sorted_results = sorted(slow_urls.items(), key=lambda t: t[1]['time'], reverse=True)[:5]
        times = map(lambda result: int(result[1]['time'] / result[1]['count']), sorted_results)
        sorted_times = list(sorted(times, key=lambda t: -t))
        return sorted_times
    else:
        stat = Counter(c).most_common(5)
        return list(map(lambda item: item[1], stat))
