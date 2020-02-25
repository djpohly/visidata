from visidata import *

class Hdf5ObjSheet(Sheet):
    'Support sheets in HDF5 format.'
    def iterload(self):
        import h5py
        source = self.source
        if isinstance(self.source, Path):
            source = h5py.File(str(self.source), 'r')

        if isinstance(source, h5py.Group):
            self.rowtype = 'sheets'
            self.columns = [
                Column(source.name, type=str, getter=lambda col,row: row.source.name.split('/')[-1]),
                Column('type', type=str, getter=lambda col,row: type(row.source).__name__),
                Column('nItems', type=int, getter=lambda col,row: len(row.source)),
            ]
            self.recalc()
            for k, v in source.items():
                subname = joinSheetnames(self.name, k)
                yield Hdf5ObjSheet(subname, source=v)
        elif isinstance(source, h5py.Dataset):
            if len(source.shape) == 1:
                self.columns = [ColumnItem(colname, colname) for colname in source.dtype.names or [0]]
                yield from source  # copy
            elif len(source.shape) == 2:  # matrix
                ncols = source.shape[1]
                self.columns = [ColumnItem('', i, width=8) for i in range(ncols)]
                self.recalc()
                yield from source  # copy
            else:
                status('too many dimensions in shape %s' % str(source.shape))
        else:
            status('unknown h5 object type %s' % type(source))


    def openRow(self, row):
        if isinstance(row, BaseSheet):
            return row
        if isinstance(row, h5py.Object):
            return H5ObjSheet(row)


Hdf5ObjSheet.addCommand('A', 'dive-metadata', 'vd.push(SheetDict(cursorRow.name + "_attrs", source=cursorRow.attrs))', 'open metadata sheet for object referenced in current row')


vd.filetype('h5', Hdf5ObjSheet)
vd.filetype('hdf5', Hdf5ObjSheet)
