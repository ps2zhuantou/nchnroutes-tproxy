produce:
	git pull
	@echo "正在下载数据源..."
	curl -f -sSL -o china_ip.conf https://raw.githubusercontent.com/misakaio/chnroutes2/master/chnroutes.txt
	curl -f -sSL -o china_ip_ipv6.conf https://ruleset-mirror.skk.moe/List/ip/china_ip_ipv6.conf
	@echo "下载完成，执行转换..."
	python3 produce.py
