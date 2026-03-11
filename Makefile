produce:
	git pull
	#curl -sSL -o china_ip.conf https://gaoyifan.github.io/china-operator-ip/china.txt
    curl -sSL -o china_ip.conf https://github.com/misakaio/chnroutes2/raw/refs/heads/master/chnroutes.txt
    curl -sSL -o china_ip_ipv6.conf https://ruleset-mirror.skk.moe/List/ip/china_ip_ipv6.conf
	#curl -sSL -o china_ip_ipv6.conf https://gaoyifan.github.io/china-operator-ip/china6.txt
	python3 produce.py
	#sudo mv routes4.conf /etc/bird/routes4.conf
	#sudo mv routes6.conf /etc/bird/routes6.conf
	#sudo birdc configure
	# sudo birdc6 configure
       
