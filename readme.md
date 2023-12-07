# ML4C (Machine Learning 4 Chem) Wiki

## Lammps customized
> Customized LAMMPS(2Aug2023) for Neural Network Potential, by AdvanceSoft Corp. <http://www.advancesoft.jp>.
### Update record
|Date|Modification|Changer|
|-|-|-|
|2023/12/07|change matgl-related path settings<br>files using self training model<br>[change ref](https://github.com/CederGroupHub/chgnet/issues/57)|ginchung|
|2023/12/06|fork|ginchung|
|-|[create](https://github.com/advancesoftcorp/lammps)|advancesoft corp.|

### Install guide
> referred notebook at [materials virtual lab](https://github.com/materialsvirtuallab/matgl/blob/main/examples/Using%20LAMMPS%20with%20MatGL.ipynb)
>
```
git clone https://github.com/Ginchung/lammps-matgl-advancesoftcorp-interface
cd lammps
mkdir build
cd build
cmake -C ../cmake/presets/basic.cmake -D BUILD_SHARED_LIBS=on -D LAMMPS_EXCEPTIONS=on -D PKG_PYTHON=on -D PKG_ML-M3GNET=on -D PKG_EXTRA-COMPUTE=on -D PKG_EXTRA-FIX=on -D PKG_MANYBODY=on -D PKG_EXTRA-DUMP=on -D PKG_MOLECULE=on ../cmake
cmake --build .
make install
```
