#include "serialization.h"
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <fstream>

Serialization::Serialization()
{
}

using namespace std;

std::string to_str(const Geo& geo)
{
//  std::vector<std::string> geo_str;
//  geo_str.reserve(GeoSize);
//  for(auto item: geo.geo)
//    geo_str.push_back(boost::lexical_cast<std::string>((int)item));
//  return boost::algorithm::join(geo_str, ";");

  std::string s;
  for(auto item: geo.geo)
  {
    s+=";"+boost::lexical_cast<std::string>((int)item);
  }
  return s;
}

std::string to_str(const Coord& c)
{
  return boost::lexical_cast<std::string>(c.x)+";"+boost::lexical_cast<std::string>(c.y);
}

int to_int(const String& s)
{
  return boost::lexical_cast<int>(s);
}

bool from_str(const std::string& line, Geo& g, Coord& c, const std::string& format)
{
  vector<string> out;
  boost::split(out, line, boost::is_any_of(";"));
  if(out.size() < 2)
    return false;
  c.x = to_int(out[0]);
  c.y = to_int(out[1]);

  if(out.size() < 7)
    return false;

  g.geo[g.O] = to_int(out[2]);
  g.geo[g.E] = to_int(out[3]);
  g.geo[g.M] = to_int(out[4]);
  g.geo[g.T] = to_int(out[5]);
  g.geo[g.S] = to_int(out[6]);
  return true;
}

bool from_csv(const String& file, GeoList& pm)
{
  ifstream ifstr(file);
  if(!ifstr.is_open())
    return false;

  string format;
  getline(ifstr, format);

  do
  {
    string line;
    getline(ifstr, line);
    Geo g;
    Coord c(-1,-1);
    if(from_str(line, g, c, ""))
      pm.push_back( std::make_pair(c, g));
  }while(!ifstr.eof());

  return true;
}

void to_csv(const GeoMesh& pm, const String& file)
{
  ofstream ofstr(file);
  if(!ofstr.is_open())
  {
    cerr <<"cannot open output file " << file << endl;
    return;
  }
  cout << "writing to " << file << endl;
  ofstr << "x;y;o;e;m;t;s\n";
  Geo g;
  auto items = pm.get_items();
  for(auto item: items)
  {
    ofstr << to_str(item.first) << to_str(item.second) << "\n";
  }
}

GeoMesh to_mesh(const GeoList& gl)
{
  GeoMesh gm;
  //gm.insert(gl.begin(), gl.end());
  return gm;
}
