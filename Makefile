produce:
	git pull
	@echo "正在下载 IPv4 数据源..."
	curl -f -sSL -o china_ip.conf https://china-operator-ip.yfgao.com/china.txt
	@echo "正在下载 IPv6 数据源..."
	curl -f -sSL -o china_ip_ipv6.conf https://china-operator-ip.yfgao.com/china6.txt
	@echo "下载完成，执行转换..."
	python3 produce.py
