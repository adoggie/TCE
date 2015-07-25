
#ifndef TCE_UTIL_BASE_64_H
#define TCE_UTIL_BASE_64_H


#include <string>
#include <vector>

namespace tce{
namespace utils{

class  Base64{
public:

    static std::string encode(const std::vector<unsigned char>&);
    static std::vector<unsigned char> decode(const std::string&);
    static bool isBase64(char);

private:

    static char encode(unsigned char);
    static unsigned char decode(char);
};

}

}


#endif
