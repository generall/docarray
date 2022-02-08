import json
import os
import random

import numpy as np
import pytest

from docarray import DocumentArray, Document
from docarray.array.sqlite import DocumentArraySqlite
from docarray.array.storage.weaviate import WeaviateConfig
from docarray.array.weaviate import DocumentArrayWeaviate


@pytest.mark.parametrize(
    'da_cls,config',
    [
        (DocumentArray, None),
        (DocumentArraySqlite, None),
        (DocumentArrayWeaviate, WeaviateConfig(n_dim=128)),
    ],
)
def test_sprite_fail_tensor_success_uri(
    pytestconfig, tmpdir, da_cls, config, start_storage
):
    files = [
        f'{pytestconfig.rootdir}/**/*.png',
        f'{pytestconfig.rootdir}/**/*.jpg',
        f'{pytestconfig.rootdir}/**/*.jpeg',
    ]
    if config:
        da = da_cls.from_files(files, config=config)
    else:
        da = da_cls.from_files(files)
    da.apply(
        lambda d: d.load_uri_to_image_tensor().set_image_tensor_channel_axis(-1, 0)
    )
    with pytest.raises(ValueError):
        da.plot_image_sprites()
    da.plot_image_sprites(tmpdir / 'sprint_da.png', image_source='uri')
    assert os.path.exists(tmpdir / 'sprint_da.png')


@pytest.mark.parametrize('image_source', ['tensor', 'uri'])
@pytest.mark.parametrize(
    'da_cls,config',
    [
        (DocumentArray, None),
        (DocumentArraySqlite, None),
        (DocumentArrayWeaviate, WeaviateConfig(n_dim=128)),
    ],
)
def test_sprite_image_generator(
    pytestconfig, tmpdir, image_source, da_cls, config, start_storage
):
    files = [
        f'{pytestconfig.rootdir}/**/*.png',
        f'{pytestconfig.rootdir}/**/*.jpg',
        f'{pytestconfig.rootdir}/**/*.jpeg',
    ]
    if config:
        da = da_cls.from_files(files, config=config)
    else:
        da = da_cls.from_files(files)
    da.apply(lambda d: d.load_uri_to_image_tensor())
    da.plot_image_sprites(tmpdir / 'sprint_da.png', image_source=image_source)
    assert os.path.exists(tmpdir / 'sprint_da.png')


def da_and_dam():
    embeddings = np.array([[1, 0, 0], [2, 0, 0], [3, 0, 0]])
    doc_array = DocumentArray(
        [
            Document(embedding=x, tags={'label': random.randint(0, 5)})
            for x in embeddings
        ]
    )

    doc_arraysq = DocumentArraySqlite(
        [
            Document(embedding=x, tags={'label': random.randint(0, 5)})
            for x in embeddings
        ]
    )

    return (doc_array, doc_arraysq)


@pytest.mark.parametrize('da', da_and_dam())
def test_plot_embeddings(da):
    p = da.plot_embeddings(start_server=False)
    assert os.path.exists(p)
    assert os.path.exists(os.path.join(p, 'config.json'))
    with open(os.path.join(p, 'config.json')) as fp:
        config = json.load(fp)
        assert len(config['embeddings']) == 1
        assert config['embeddings'][0]['tensorShape'] == list(da.embeddings.shape)


@pytest.mark.parametrize(
    'da_cls,config_gen',
    [
        (DocumentArray, None),
        (DocumentArraySqlite, None),
        (DocumentArrayWeaviate, lambda: WeaviateConfig(n_dim=5)),
    ],
)
def test_plot_embeddings_same_path(tmpdir, da_cls, config_gen, start_storage):
    if config_gen:
        da1 = da_cls.empty(100, config=config_gen())
        da2 = da_cls.empty(768, config=config_gen())
    else:
        da1 = da_cls.empty(100)
        da2 = da_cls.empty(768)
    da1.embeddings = np.random.random([100, 5])
    p1 = da1.plot_embeddings(start_server=False, path=tmpdir)
    da2.embeddings = np.random.random([768, 5])
    p2 = da2.plot_embeddings(start_server=False, path=tmpdir)
    assert p1 == p2
    assert os.path.exists(p1)
    with open(os.path.join(p1, 'config.json')) as fp:
        config = json.load(fp)
        assert len(config['embeddings']) == 2


@pytest.mark.parametrize(
    'da_cls,config',
    [
        (DocumentArray, None),
        (DocumentArraySqlite, None),
        (DocumentArrayWeaviate, WeaviateConfig(n_dim=128)),
    ],
)
def test_summary_homo_hetero(da_cls, config, start_storage):
    if config:
        da = da_cls.empty(100, config=config)
    else:
        da = da_cls.empty(100)
    da._get_attributes()
    da.summary()

    da[0].pop('id')
    da.summary()


@pytest.mark.parametrize(
    'da_cls,config',
    [
        (DocumentArray, None),
        (DocumentArraySqlite, None),
        (DocumentArrayWeaviate, WeaviateConfig(n_dim=128)),
    ],
)
def test_empty_get_attributes(da_cls, config, start_storage):
    if config:
        da = da_cls.empty(10, config=config)
    else:
        da = da_cls.empty(10)
    da[0].pop('id')
    print(da[:, 'id'])
