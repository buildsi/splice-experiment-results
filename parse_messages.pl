use strict;
use warnings;

die "Usage: $0 file" unless @ARGV == 1;

open my $fdOut, '<', $ARGV[0] or die "Unable to open '$ARGV[0]': $!\n";

my $num_libs=0;
my %counts;

run();

local $\ = "\n";
print "Total libs: $num_libs";
print "abigail total: $counts{'libabigail'}{'count'}";
print "abigail SONAME changed:";
print "    total: $counts{'libabigail'}{'soname_changed'}{'count'}";
print "    Functions:";
print "          total: $counts{'libabigail'}{'soname_changed'}{'func'}{'count'}";
print "        removed: $counts{'libabigail'}{'soname_changed'}{'func'}{'removed'}";
print "        changed: $counts{'libabigail'}{'soname_changed'}{'func'}{'changed'}";
print "          added: $counts{'libabigail'}{'soname_changed'}{'func'}{'added'}";
print "    Variables:";
print "          total: $counts{'libabigail'}{'soname_changed'}{'var'}{'count'}";
print "        removed: $counts{'libabigail'}{'soname_changed'}{'var'}{'removed'}";
print "        changed: $counts{'libabigail'}{'soname_changed'}{'var'}{'changed'}";
print "          added: $counts{'libabigail'}{'soname_changed'}{'var'}{'added'}";
print "abigail SONAME unchanged:";
print "    total: $counts{'libabigail'}{'soname_unchanged'}{'count'}";
print "    Functions:";
print "          total: $counts{'libabigail'}{'soname_unchanged'}{'func'}{'count'}";
print "        removed: $counts{'libabigail'}{'soname_unchanged'}{'func'}{'removed'}";
print "        changed: $counts{'libabigail'}{'soname_unchanged'}{'func'}{'changed'}";
print "          added: $counts{'libabigail'}{'soname_unchanged'}{'func'}{'added'}";
print "    Variables:";
print "          total: $counts{'libabigail'}{'soname_unchanged'}{'var'}{'count'}";
print "        removed: $counts{'libabigail'}{'soname_unchanged'}{'var'}{'removed'}";
print "        changed: $counts{'libabigail'}{'soname_unchanged'}{'var'}{'changed'}";
print "          added: $counts{'libabigail'}{'soname_unchanged'}{'var'}{'added'}";
print '-'x20;
print "abilab total: ", $counts{'abilab'}{'count'}||0;
print "    no debug: ", $counts{'abilab'}{'nodebug'}||0;
print '-'x20;
print "symbols total: $counts{'symbols'}{'count'}";
print "      no _chk: $counts{'symbols'}{'missing_chk'}";

sub run {
	my $file;
	while(<$fdOut>) {
		chomp;
		if(/^FILE--/) {
			$file=$_;
			$num_libs++;
			next;
		}
		
		if(/^libabigail/) {
			$counts{'libabigail'}{'count'}++;
			if(/ELF SONAME changed/) {
				$counts{'libabigail'}{'soname_changed'}{'count'}++;
				if(/Functions changes summary/) {
					/Functions changes summary: (\d+) Removed, (\d+) Changed.*?, (\d+) Added/;
					$counts{'libabigail'}{'soname_changed'}{'func'}{'count'} += ($1+$2+$3)>0;
					$counts{'libabigail'}{'soname_changed'}{'func'}{'removed'} += ($1>0);
					$counts{'libabigail'}{'soname_changed'}{'func'}{'changed'} += ($2>0);
					$counts{'libabigail'}{'soname_changed'}{'func'}{'added'} += ($3>0);
				}
				if(/Variables changes summary/) {
					/Variables changes summary: (\d+) Removed, (\d+) Changed.*?, (\d+) Added/;
					$counts{'libabigail'}{'soname_changed'}{'var'}{'count'} += ($1+$2+$3)>0;
					$counts{'libabigail'}{'soname_changed'}{'var'}{'removed'} += ($1>0);
					$counts{'libabigail'}{'soname_changed'}{'var'}{'changed'} += ($2>0);
					$counts{'libabigail'}{'soname_changed'}{'var'}{'added'} += ($3>0);
				}
			} else {
				$counts{'libabigail'}{'soname_unchanged'}{'count'}++;
				if(/Functions changes summary/) {
					/Functions changes summary: (\d+) Removed, (\d+) Changed.*?, (\d+) Added/;
					$counts{'libabigail'}{'soname_unchanged'}{'func'}{'count'} += ($1+$2+$3)>0;
					$counts{'libabigail'}{'soname_unchanged'}{'func'}{'removed'} += ($1>0);
					$counts{'libabigail'}{'soname_unchanged'}{'func'}{'changed'} += ($2>0);
					$counts{'libabigail'}{'soname_unchanged'}{'func'}{'added'} += ($3>0);
				}
				if(/Variables changes summary/) {
					/Variables changes summary: (\d+) Removed, (\d+) Changed.*?, (\d+) Added/;
					$counts{'libabigail'}{'soname_unchanged'}{'var'}{'count'} += ($1+$2+$3)>0;
					$counts{'libabigail'}{'soname_unchanged'}{'var'}{'removed'} += ($1>0);
					$counts{'libabigail'}{'soname_unchanged'}{'var'}{'changed'} += ($2>0);
					$counts{'libabigail'}{'soname_unchanged'}{'var'}{'added'} += ($3>0);
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
}