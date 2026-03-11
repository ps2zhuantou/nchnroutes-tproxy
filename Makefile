produce:
	git pull
	@echo "正在下载数据源..."
	curl -f -sSL -o https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt
	curl -f -sSL -o china_ip_ipv6.conf https://gaoyifan.github.io/china-operator-ip/china6.txt
	@echo "下载完成，执行转换..."
	python3 produce.py
