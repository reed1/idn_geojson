-- dump to box/prov.csv

select
  id,
  nama,
  doc->>'kode_old' as kode
from wilayah
where parent_id = 0 and level = 'provinsi'

-- dump to box/kab.csv

select
  w1.id as prov_id,
  w1.nama as prov_nama,
  w1.doc->>'kode_old' as prov_kode,
  w2.id as kab_id,
  w2.nama as kab_nama,
  w2.doc->>'kode_old' as kab_kode
from (
  select * from wilayah
  where parent_id = 0 and level = 'provinsi'
) as w1
inner join wilayah as w2 on
  w2.parent_id = w1.id and w2.level = 'kabupaten'
