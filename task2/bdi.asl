//type(_).
solution(0).
satisfied(false).

!start.

+!start <-
  .print("starting belief agent");
  .wait(1000);
  +satisfied(false);
  !selection.



//!selection.

+!solution: solution \== 0
  <- .print("got here").

// no idea how to get this working
//+!selection: solution(X) == 0
//+!selection: satisfied() == false  
+!selection: true  
  <-
  .print("Starting solution selection");
  !select.


+!select: type(obj1)
  <- 
    .print("obj1 preferring selection belief");
    ?sols(Y);
    //+sols(Y);
    .selector(0, Y, R);
    .print("selected sol", R);
    .result(R);
    .wait(5000);
    +solution(R).
    //!select.

+!select: type(obj2)
  <- 
    .print("obj2 preferring selection belief");
    ?sols(Y);
    //+sols(Y);
    .selector(1, Y, R);
    .print("selected sol", R);
    .result(R);
    .wait(5000);
    +solution(R).
    //!select.

+!select: type(nondom)
  <- 
    .print("non dominatation preferring selection belief");
    ?sols(Y);
    //+sols(Y);
    .non_dom(1, Y, R);
    .print("selected sol", R);
    .result(R);
    .wait(5000);
    +solution(R).
    //!select.

+!select: type(refpoint) // also check that ref_point exists maybe
  <- 
    .print("preference point preferring selection belief");
    //?sols(Y);
    //+sols(Y);
    ?refpoint(P,Y);
    //+refpoint(P);
    .refpoint(P, Y, R);
    .print("selected sol", R);
    .result(R);
    .wait(5000);
    +solution(R).
    //!select.


+!select: not type(_)
  <-
    .print("waiting for belief about selection");
    .wait(2000);
    !select.

+refpoint(P)
  <- .print("refpoint is", P).

// dont print solution if its 0, the og value
+solution(X): X \== 0
  <- .print("sol is", X);
  .wait(1000);
  -solution(X);
  +solution(0);
  !selection.

+sols(Y)
  <- .print("all sols are:", Y).

+!satisfied(T) 
  <- .print("DM satisfied");
    +satisfied(true).
