Vagrant.configure("2") do |config|
  config.vm.synced_folder '.', '/vagrant'
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.network "private_network", ip: "192.168.56.100"

  config.vm.define "shorturl" do |t|
  	  config.vm.provider "virtualbox" do |vb|
	     vb.cpus = "2"
	     vb.memory = "1024"
	     vb.name = "shorturl"
	  end
	  config.vm.provision "shell", inline: <<-SHELL
		export mysql_pass='test1234'
		debconf-set-selections <<< 'mysql-server mysql-server/root_password password '$mysql_pass
		debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password '$mysql_pass
		apt-get update
		apt-get install -y mysql-server python-pip git
		pip install flask pymysql
		git clone https://github.com/s012ja/shorturl.git /vagrant/shorturl/
		mysql -uroot -p$mysql_pass < /vagrant/shorturl/shorturl.sql
	  SHELL
  end
end
