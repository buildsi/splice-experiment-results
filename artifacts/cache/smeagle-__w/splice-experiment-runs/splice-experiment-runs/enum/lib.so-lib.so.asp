
%============================================================================
% Library Facts
%============================================================================

%----------------------------------------------------------------------------
% Library: /__w/splice-experiment-runs/splice-experiment-runs/enum/lib.so
%----------------------------------------------------------------------------
abi_typelocation("a","_Z3foo14ColorClassEnum","Import","Integer32","%rdi").
abi_typelocation("a","_Z11print_color5Color","Import","Integer32","%rdi").
abi_typelocation("a","_Z11print_color5Color","Export","Integer32","%rax").
abi_typelocation("a","_Z8enumfunc8CharEnum","Import","Integer8","%rdi").
abi_typelocation("a","_Z8boolfunc8BoolEnum","Import","Integer8","%rdi").
abi_typelocation("a","_Z8sizefunc8SizeEnum","Import","Integer64","%rdi").

%----------------------------------------------------------------------------
% Library: /__w/splice-experiment-runs/splice-experiment-runs/enum/breaks/add_to_sizeenum/lib.so
%----------------------------------------------------------------------------
abi_typelocation("b","_Z3foo14ColorClassEnum","Import","Integer32","%rdi").
abi_typelocation("b","_Z11print_color5Color","Import","Integer32","%rdi").
abi_typelocation("b","_Z11print_color5Color","Export","Integer32","%rax").
abi_typelocation("b","_Z8enumfunc8CharEnum","Import","Integer8","%rdi").
abi_typelocation("b","_Z8boolfunc8BoolEnum","Import","Integer8","%rdi").
abi_typelocation("b","_Z8sizefunc8SizeEnum","Import","Integer64","%rdi").
