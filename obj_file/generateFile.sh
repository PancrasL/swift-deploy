python3 init-file.py 1kb 1024 26
python3 init-file.py 10kb 10240 26
python3 init-file.py 100kb 10240 26
python3 init-file.py 1mb 1048576 26

. admin-openrc
openstack object create test 1kb 10kb 100kb 1mb 10mb 100mb