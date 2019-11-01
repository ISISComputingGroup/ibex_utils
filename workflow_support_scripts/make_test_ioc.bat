@echo off

call make_ioc %1 %2
pushd C:\Instrument\Apps\EPICS\support\IocTestFramework\master
python run_tests.py -t %3 -a
popd
