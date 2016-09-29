pwd
cd payplanner/
ll
cd templates/
ll
rm -f *copy
ll
vi config.html 
ll
sudo cp /home/ec2-user/config.html.new config.html
ll
cat config.html 
cd ..
pwd
l
ll
sudo cp /home/ec2-user/forms.new forms.py
ll
cat forms.py
sudo systemctl restart httpd.service
pwd
cd ../GreenPrint/
ll
sudo cp settings.py /home/ec2-user/settings_prod.py
exit
pwd
whoami
exit
sudo vi /etc/bashrc
sudo vi /etc/profile
pwd
cd GreenPrint/
ll
vi settings.py
sudo vi /etc/profile
vi settings.py
sudo systemctl restart httpd.service
sudo tail /var/log/httpd/error_log
exit
echo $DJANGO_KEY
sudo systemctl restart httpd.service
sudo tail /var/log/httpd/error_log
python
grep DJ /etc/profile
grep DJ /etc/profile >> /etc/basrc
sudo grep DJ /etc/profile >> /etc/basrc
sudo vi /etc/bashrc
sudo vi /etc/profile
sudo systemctl restart httpd.service
echo $DJANGO_KEY
sudo tail /var/log/httpd/error_log
python
cd GreenPrint/
vi wsgi.py 
vi wsgi
vi wsgi.py 
cd /etc/httpd/conf.d
ll
vi django
sudo vi django.conf
cd /etc/sysconfig
ll
cd /etc/enviroment
cat /etc/enviroment
cat /etc/environment
ll /etc/environment 
grep DJ /etc/profile
sudo grep DJ /etc/profile >> /etc/environment 
sudo grep DJ /etc/profile >> sudo /etc/environment 
su 
sudo su
pwd
cd ~
pwd
cd GreenPrint/
vi settings.py
python
pwd
whoami
sudo mv /etc/default/django.py pp_settings.py
ll /etc/default/
ll
sudo mv pp_settings.py /etc/default/
ll /etc/default/
python
pwd
vi settings.py
sudo systemctl restart httpd.service
pwd
cd ..
pwd
python manage.py shell
pwd
ll
cd GreenPrint/
vi settings.py
grep SECRET settings.py
sudo systemctl restart httpd.service
pwd
cd ..
ll
ll GreenPrint/
cd GreenPrint/
ll
rm -f urls_copy 
rm -f urls.py.copy 
ll
cd ..
ll
sudo cp GreenPrint/settings.py ~ec2-user/settings_prod.py
whoami
pwd
ll /home/ec2-user/
sudo ll /home/ec2-user/
sudo ls -l /home/ec2-user/
whoami
exit
