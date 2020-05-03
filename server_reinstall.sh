pip3 uninstall deeplabcut
python3 setup.py sdist bdist_wheel
pip3 install dist/deeplabcut-2.1.6.2-py3-none-any.whl
rm -rf /Users/salvi/opt/anaconda3/envs/DLC-CPU/lib/python3.7/site-packages/deeplabcut
rm -rf /Users/salvi/opt/anaconda3/envs/DLC-CPU/lib/python3.7/site-packages/deeplabcut.egg-info
tar -zxvf dist/deeplabcut-2.1.6.2.tar.gz --directory dist
mv dist/deeplabcut-2.1.6.2/deeplabcut /Users/salvi/opt/anaconda3/envs/DLC-CPU/lib/python3.7/site-packages/deeplabcut
mv dist/deeplabcut-2.1.6.2/deeplabcut.egg-info /Users/salvi/opt/anaconda3/envs/DLC-CPU/lib/python3.7/site-packages/deeplabcut.egg-info
