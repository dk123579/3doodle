from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


def _model_xml(width: float, depth: float, height: float) -> str:
    # A minimal watertight rectangular prism mesh.
    vertices = [
        (0, 0, 0),
        (width, 0, 0),
        (width, depth, 0),
        (0, depth, 0),
        (0, 0, height),
        (width, 0, height),
        (width, depth, height),
        (0, depth, height),
    ]

    triangles = [
        (0, 1, 2),
        (0, 2, 3),
        (4, 6, 5),
        (4, 7, 6),
        (0, 4, 5),
        (0, 5, 1),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 4),
        (3, 4, 0),
    ]

    vertices_xml = "\n".join(
        f'          <vertex x="{x}" y="{y}" z="{z}" />' for x, y, z in vertices
    )
    triangles_xml = "\n".join(
        f'          <triangle v1="{a}" v2="{b}" v3="{c}" />' for a, b, c in triangles
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
{vertices_xml}
        </vertices>
        <triangles>
{triangles_xml}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>
'''


def create_box_3mf(width: float, depth: float, height: float) -> bytes:
    """Create a minimal, slicer-ready 3MF package containing a single box mesh."""
    model = _model_xml(width, depth, height)
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
'''
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
'''

    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("3D/3dmodel.model", model)

    return buffer.getvalue()
