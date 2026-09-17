#include "cylindermesh.h"
#include "basepart.h"
#include <raylib.h>

static Color rl_from_color3(Color3 col, float transparency)
{
    return (Color){col.R * 255, col.G * 255, col.B * 255, (1.0f-transparency) * 255};
}

void draw_cylindermesh(CylinderMesh *this, BasePart *part)
{
    Color3 vertexColor = part->Color;
    DataModelMesh *dmmesh = this;
    DrawCylinder(
        Vector3Add(part->Position, dmmesh->Offset),
        part->size.x + dmmesh->Scale.x,
        part->size.x + dmmesh->Scale.x,
        part->size.y + dmmesh->Scale.y,
        12, rl_from_color3(vertexColor, 0.0f));
}

static void cylinder_mesh_draw(DataModelMesh *this, BasePart *part)
{
    draw_cylindermesh((CylinderMesh *)this, part);
}

CylinderMesh *CylinderMesh_new(const char *className, Instance *parent)
{
    CylinderMesh *newInst = BevelMesh_new("CylinderMesh", parent);

    newInst->bevelmesh.datamodelmesh.instance.DataCost = sizeof(CylinderMesh);
    newInst = realloc(newInst, sizeof(CylinderMesh));

    newInst->bevelmesh.datamodelmesh.drawFunc = cylinder_mesh_draw;

    return newInst;
}

void serialize_CylinderMesh(CylinderMesh *cylindermesh, SerializeInstance *inst)
{
    serialize_BevelMesh(cylindermesh, inst);
}
