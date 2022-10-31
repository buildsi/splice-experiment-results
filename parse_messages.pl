use strict;
use warnings;

die "Usage: $0 file" unless @ARGV == 1;

open my $fdOut, '<', $ARGV[0] or die "Unable to open '$ARGV[0]': $!\n";

my $num_libs=0;
my %counts;
while(<$fdOut>) {
	chomp;
	if(/^FILE--/) {
		$num_libs++;
		next;
	}
	
	if(/^libabigail/) {
		$counts{'libabigail'}{'count'}++;
		my $soname = (/ELF SONAME changed/) ? 'soname_changed' : 'soname_unchanged';
		$counts{'libabigail'}{$soname}{'count'}++;
		if(/Functions changes summary/) {
			/Functions changes summary: (\d+) Removed.*?, (\d+) Changed.*?, (\d+) Added.*? function[s]?/;
			&_update_abigail($soname, 'func', $1, $2, $3);
		}
		if(/Function symbols changes summary/) {
			/Function symbols changes summary: (\d+) Removed.*?, (\d+) Added.*? function symbol[s]? not referenced by debug info/;
			&_update_abigail_syms($soname, 'funcsyms', $1, $2);
		}
		if(/functions with some indirect sub-type change/) {
			/(\d+) function[s]? with some indirect sub-type change/;
			$counts{'libabigail'}{$soname}{'func'}{'subtype_changed'}{'count'}++;
		}
		if(/Variables changes summary/) {
			/Variables changes summary: (\d+) Removed.*?, (\d+) Changed.*?, (\d+) Added.*?/;
			&_update_abigail($soname, 'var', $1, $2, $3);
		}
		if(/Variable symbols changes summary/) {
			/Variable symbols changes summary: (\d+) Removed.*?, (\d+) Added.*? variable symbol[s]? not referenced by debug info/;
			&_update_abigail_syms($soname, 'varsyms', $1, $2);
		}
		if(/this (.+)? a new entry to the vtable of class/) {
			$counts{'libabigail'}{$soname}{'vtable'}{'count'}++;
			my $action = $1;
			if($action =~ /add/) {
				$counts{'libabigail'}{$soname}{'vtable'}{'added'}++;
			}
			if($action =~ /remove/) {
				$counts{'libabigail'}{$soname}{'vtable'}{'removed'}++;
			}
		}
		if(/\d+\s+enumerator\s+(.+)?\:/) {
		  my $action = $1;
		  $counts{'libabigail'}{$soname}{'enumerator'}{'count'}++;
		  if($action =~ /change/) {
				$counts{'libabigail'}{$soname}{'enumerator'}{'changed'}++;
			}
			if($action =~ /deletion/) {
				$counts{'libabigail'}{$soname}{'enumerator'}{'removed'}++;
			}
			if($action =~ /insertion/) {
				$counts{'libabigail'}{$soname}{'enumerator'}{'added'}++;
			}
		}
	} elsif(/^abi-laboratory/) {
		$counts{'abilab'}{'count'}++;
		if(/ERROR\: can\'t find debug info in object/) {
			$counts{'abilab'}{'nodebug'}++;
		}
	} elsif(/^missing-previously-found-symbols/) {
		$counts{'symbols'}{'count'}++;
		if(/\b.+_chk\b/) {
			$counts{'symbols'}{'missing_chk'}++;
		}
	}
}

sub _update_abigail {
	my ($soname, $category, $f1, $f2, $f3) = @_;
	$counts{'libabigail'}{$soname}{$category}{'count'} += ($f1+$f2+$f3)>0;
	$counts{'libabigail'}{$soname}{$category}{'removed'}{'any'} += ($f1>0);
	$counts{'libabigail'}{$soname}{$category}{'removed'}{'only'} += ($f1>0&&$f2==0&&$f3==0);
	$counts{'libabigail'}{$soname}{$category}{'changed'}{'any'} += ($f2>0);
	$counts{'libabigail'}{$soname}{$category}{'changed'}{'only'} += ($f1==0&&$f2>0&&$f3==0);
	$counts{'libabigail'}{$soname}{$category}{'added'}{'any'} += ($f3>0);
	$counts{'libabigail'}{$soname}{$category}{'added'}{'only'} += ($f1==0&&$f2==0&&$f3>0);
}
sub _update_abigail_syms {
	my ($soname, $category, $f1, $f2) = @_;
	$counts{'libabigail'}{$soname}{$category}{'count'} += ($f1+$f2)>0;
			$counts{'libabigail'}{$soname}{$category}{'removed'}{'any'} += ($f1>0);
			$counts{'libabigail'}{$soname}{$category}{'removed'}{'only'} += ($f1>0&&$f2==0);
			$counts{'libabigail'}{$soname}{$category}{'added'}{'any'} += ($f2>0);
			$counts{'libabigail'}{$soname}{$category}{'added'}{'only'} += ($f1==0&&$f2>0);
}

local $\ = "\n";
print "Total libs: $num_libs";
print "abigail total: $counts{'libabigail'}{'count'}";
for my $soname ('soname_changed', 'soname_unchanged') {
	print "abigail SONAME $soname:";
	print "    total: $counts{'libabigail'}{$soname}{'count'}";
	print "    Functions:";
	my $tmp = $counts{'libabigail'}{$soname}{'func'};
	print "          total: $tmp->{'count'}";
	print "        removed: $tmp->{'removed'}{'any'},$tmp->{'removed'}{'only'}";
	print "        changed: $tmp->{'changed'}{'any'},$tmp->{'changed'}{'only'}";
	print "          added: $tmp->{'added'}{'any'},$tmp->{'added'}{'only'}";
		print "    Function subtype changes:";
	print "          total: ", $tmp->{'subtype_changed'}{'count'}||0;
	print "    Virtual Table modified:";
	print "          total: ", $counts{'libabigail'}{$soname}{'vtable'}{'count'}||0;
	print "          added: ", $counts{'libabigail'}{$soname}{'vtable'}{'added'}||0;
	print "        removed: ", $counts{'libabigail'}{$soname}{'vtable'}{'removed'}||0;
	print "    Enumerator changes:";
	print "          total: ", $counts{'libabigail'}{$soname}{'enumerator'}{'count'}||0;
	print "          added: ", $counts{'libabigail'}{$soname}{'enumerator'}{'added'}||0;
	print "        removed: ", $counts{'libabigail'}{$soname}{'enumerator'}{'removed'}||0;
	print "        changed: ", $counts{'libabigail'}{$soname}{'enumerator'}{'changed'}||0;
	print "    Function symbols:";
	$tmp = $counts{'libabigail'}{$soname}{'funcsyms'};
	print "          total: $tmp->{'count'}";
	print "        removed: $tmp->{'removed'}{'any'},$tmp->{'removed'}{'only'}";
	print "          added: $tmp->{'added'}{'any'},$tmp->{'added'}{'only'}";
	print "    Variables:";
	$tmp = $counts{'libabigail'}{$soname}{'var'};
	print "          total: $tmp->{'count'}";
	print "        removed: $tmp->{'removed'}{'any'},$tmp->{'removed'}{'only'}";
	print "        changed: $tmp->{'changed'}{'any'},$tmp->{'changed'}{'only'}";
	print "          added: $tmp->{'added'}{'any'},$tmp->{'added'}{'only'}";
	print "    Variable symbols:";
	$tmp = $counts{'libabigail'}{$soname}{'varsyms'};
	print "          total: $tmp->{'count'}";
	print "        removed: $tmp->{'removed'}{'any'},$tmp->{'removed'}{'only'}";
	print "          added: $tmp->{'added'}{'any'},$tmp->{'added'}{'only'}";
}
print '-'x20;
print "abilab total: ", $counts{'abilab'}{'count'}||0;
print "    no debug: ", $counts{'abilab'}{'nodebug'}||0;
print '-'x20;
print "symbols total: $counts{'symbols'}{'count'}";
print "      no _chk: $counts{'symbols'}{'missing_chk'}";
