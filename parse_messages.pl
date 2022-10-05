use strict;
use warnings;

die "Usage: $0 file" unless @ARGV == 1;

open my $fdOut, '<', $ARGV[0] or die "Unable to open '$ARGV[0]': $!\n";

my $num_libs=0;
my $libabigail=0;
my $libabigail_changed_soname=0;
my $libabigail_changed_other=0;
my $abilab=0;
my $abilab_nodebug=0;
my $symbols=0;
my $symbols_chk=0;

my $file;

while(<$fdOut>) {
	chomp;
	if(/^FILE--/) {
		$file=$_;
		$num_libs++;
		next;
	}
	
	if(/^libabigail/) {
		$libabigail++;
		if(/ELF SONAME changed/) {
			$libabigail_changed_soname++;
			
			if(/Functions changes summary/) {
				/Functions changes summary: (\d+) Removed, (\d+) Changed.*?, (\d+) Added/;
				$libabigail_changed_other += ($1+$2+$3)>0;
			}
			if(/Variables changes summary/) {
				/Variables changes summary: (\d+) Removed, (\d+) Changed.*?, (\d+) Added/;
				$libabigail_changed_other += ($1+$2+$3)>0;
			}
		}
	} elsif(/^abi-compliance-tester/) {
		$abilab++;
		if(/ERROR\: can\'t find debug info in object/) {
			$abilab_nodebug++;			
		}
	} elsif(/^missing-previously-found-symbols/) {
		$symbols++;
		if(/\b.+_chk\b/) {
			$symbols_chk++;
		}
	}
}

print<<END
Total libs: $num_libs
abigail total: $libabigail
abigail SONAME total: $libabigail_changed_soname
abigail SONAME and other: $libabigail_changed_other
abilab total: $abilab
abilab nodebug: $abilab_nodebug
symbols total: $symbols
symbols _chk: $symbols_chk
END