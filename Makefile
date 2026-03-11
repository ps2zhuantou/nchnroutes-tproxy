produce:
	git pull
	@echo "正在下载数据源..."
	curl -f -sSL -o https://github.com/zccing/china_route/raw/refs/heads/main/cidrs/raw/china_cidr.txt
	curl -f -sSL -o china_ip_ipv6.conf https://gaoyifan.github.io/china-operator-ip/china6.txt
	@echo "下载完成，执行转换..."
	python3 produce.py
