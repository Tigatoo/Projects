#include "chess.h"

#include<iostream>
#include<tuple>
#include <set>


using namespace std;

//copied from stackoverflow
//defines addition operator for tuples
namespace internal
{
    //see: https://stackoverflow.com/a/16387374/4181011
    template<typename T, size_t... Is>
    void add_rhs_to_lhs(T& t1, const T& t2, std::integer_sequence<size_t, Is...>)
    {
        auto l = { (std::get<Is>(t1) += std::get<Is>(t2), 0)... };
        (void)l; // prevent unused warning
    }
}

template <typename...T>
std::tuple<T...>& operator += (std::tuple<T...>& lhs, const std::tuple<T...>& rhs)
{
    internal::add_rhs_to_lhs(lhs, rhs, std::index_sequence_for<T...>{});
    return lhs;
}

template <typename...T>
std::tuple<T...> operator + (std::tuple<T...> lhs, const std::tuple<T...>& rhs)
{
   return lhs += rhs;
}

//class defining the main properties of a piece
class Piece{
  public:
  //type of piece stored as a char (e.g. Q for queen)
  char type;
  //current position
  tuple<int, int> position;
  //moves specific to the piece type
  set<tuple<int, int>> move_set;
  //moves currently allowed (depends on board configuration)
  set<tuple<int, int>> allowed_moves;
  //colour
  string colour;

  //remove forbidden moves
  //PRE: takes a set which is assumed to be a subset of the allowed moves
  void remove_moves(set<tuple<int, int>>& forbidden_moves){
    set<tuple<int, int>> new_allowed;

    set<tuple<int, int>>::iterator itr_f, itr_a;

    for(itr_a = allowed_moves.begin(); itr_a != allowed_moves.end(); itr_a++){
      bool forbidden = false;
      for(itr_f = forbidden_moves.begin(); itr_f != forbidden_moves.end(); itr_f++){
        if(*itr_f == *itr_a){
          forbidden = true;
          break;
        };
      };
      if(!forbidden){
        new_allowed.insert(*itr_a);
      };
    };
    allowed_moves = new_allowed;
  };
};

//From here on all types of pieces are defined
class Queen: private Piece{

};


int main(){

  Piece testObj;
  tuple<int, int> v1, v2, v3, v4;
  v1 = make_tuple(1,1);
  v2 = make_tuple(2,3);
  v3 = make_tuple(4,5);
  v4 = make_tuple(1,1);

  testObj.allowed_moves.insert(v1);
  testObj.allowed_moves.insert(v2);
  testObj.allowed_moves.insert(v3);

  set<tuple<int, int>> a, b;
  a.insert(v1);
  testObj.remove_moves(a);

  set<tuple<int, int>>::iterator it;
  //it = std::set_difference(testObj.allowed_moves.begin(), testObj.allowed_moves.end(),
  //                   a.begin(), a.end(), b.begin())
  for(it = testObj.allowed_moves.begin(); it != testObj.allowed_moves.end(); it++){
    cout << '<' << get<0>(*it) << ',' << get<1>(*it) << "> \n";
  }
  return 0;
};
