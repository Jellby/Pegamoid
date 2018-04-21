Bootstrap: docker
From: python:3.4-slim

%help
Pegamoid is an orbital viewer
Use the -vgl option to run with vglrun

%post
# update apt for installing packages
apt-get update
# install packages needed for compiling pyside
deps="wget make cmake gcc g++ qt4-default"
apt-get install -y --no-install-recommends $deps
# install packages needed for OpenGL and vglrun
apt-get install -y --no-install-recommends libqtgui4 mesa-utils libgl1-mesa-dri libxv1
# install vglrun
wget https://downloads.sourceforge.net/project/virtualgl/2.5.2/virtualgl_2.5.2_amd64.deb
dpkg -i virtualgl_2.5.2_amd64.deb
rm virtualgl_2.5.2_amd64.deb
# install required python packages
pip install --upgrade pip
pip install qtpy pyside vtk numpy h5py
# remove build dependencies
apt-get purge -y --auto-remove $deps

%files
pegamoid.py /bin

%runscript
ulimit -c 0
if [ "$1" = "-vgl" ]; then
  shift
  vglrun python /bin/pegamoid.py "$@"
else
  python /bin/pegamoid.py "$@"
fi
