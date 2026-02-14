produce:
	git pull
	curl -o delegated-apnic-latest https://ftp.apnic.net/stats/apnic/delegated-apnic-latest
	curl -o china_ip_list.txt https://raw.githubusercontent.com/misakaio/chnroutes2/master/chnroutes.txt
        #curl -o china_ip_list.txt https://raw.githubusercontent.com/17mon/china_ip_list/master/china_ip_list.txt
        #curl -o china_ip_list.txt https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/text/cn.txt
        #curl -o china_ip_list.txt https://china-operator-ip.yfgao.com/china.txt
        #curl -o china_ip_list.txt https://raw.githubusercontent.com/zhengkai/chn-ip/refs/heads/master/ipv4.txt
        #curl -o china_ip_list.txt https://raw.githubusercontent.com/metowolf/iplist/master/data/special/china.txt
        #curl -o china_ip_list.txt https://raw.githubusercontent.com/gaoyifan/china-operator-ip/refs/heads/ip-lists/china.txt
        #curl -o china_ip_list.txt https://raw.githubusercontent.com/mayaxcn/china-ip-list/refs/heads/master/chnroute.txt
        #curl -o china_ip_list.txt https://raw.githubusercontent.com/carrnot/china-ip-list/release/ipv4.txt
        #curl -o  china_ip_list.txt https://raw.githubusercontent.com/billkit/CN-IP/refs/heads/main/all_cn_cidr.txt
	python3 produce.py
	#sudo mv routes4.conf /etc/bird/routes4.conf
	#sudo mv routes6.conf /etc/bird/routes6.conf
	#sudo birdc configure
	# sudo birdc6 configure
       
