#ifndef SERIALIZATION_H
#define SERIALIZATION_H

class Serialization
{
public:
    Serialization();
};

#include "Data.h"
void to_csv(const GeoMesh& pm, const String& file);
bool from_csv(const String& file, GeoList& pm);
GeoMesh to_mesh(const GeoList& gl);

#endif // SERIALIZATION_H
