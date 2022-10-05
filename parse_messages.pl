use strict;
use warnings;

die "Usage: $0 file" unless @ARGV == 1;

open my $fdOut, '<', $ARGV[0] or die "Unable to open '$ARGV[0]': $!\n";

if($ARGV[0] !~ /\.disagreement$/) {
	&parse_abigail()
} else {
	$ARGV[0] =~ /.+\..+\.(.+)\.(.+)\.messages.disagreement/;
	if($1 eq 'abidiff') {
		&parse_abigail();
	} elsif($1 eq 'abi-compliance-tester') {
		&parse_abilab();
	} elsif($1 eq 'missing-previously-found-symbols') {
		&parse_symbols();
	} elsif($1 eq 'missing-previously-found-symbols') {
		&parse_exports();
	}
}

sub parse_abilab {
	my $other_pred = shift;
	my $num_libs=0;
	my ($abilib,$symbols,$exports)=(0,0,0);
	
	while(<$fdOut>) {
		chomp;
		if(/^FILE--/) {
			$num_libs++;
			next;
		}
		if(/^abi-laboratory/) {
			$abilib++;
		} elsif(/^missing-previously-found-symbols/) {
			$symbols++;
		} elsif(/^missing-previously-found-exports/) {
			$exports++;
		}
	}

	local $\ = '\n';
	print "Total libs: $num_libs";
	if($other_pred eq 'missing-previously-found-symbols') {
		print "symbols: $symbols\n";
	} elsif ($other_pred eq 'missing-previously-found-exports') {
		print "exports: $exports\n";
	}
}

sub parse_symbols {}

sub parse_exports {}

sub parse_abigail {
	my $num_libs=0;
	my $libabigail=0;
	my $libabigail_changed_soname=0;
	my $libabigail_changed_other=0;
	
	while(<$fdOut>) {
		chomp;
		if(/^FILE--/) {
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
		}
	}

	print<<END
Total libs: $num_libs
abigail total: $libabigail
abigail SONAME total: $libabigail_changed_soname
abigail SONAME and other: $libabigail_changed_other
END
}