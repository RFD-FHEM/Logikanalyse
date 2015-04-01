#!/usr/bin/perl

my $msg = "AS6002e00ce\n";
print $msg;
print "Model:";
my $model = sprintf("%01d", substr($msg,2,1));
print $model."\n";
my $hextext = substr($msg,3);###
my $hexlen = length($hextext);###
print $hextext;###
print $hexlen;###
print "\n";
$SensorTyp = "ASLight";
$channel = 0;
print substr($msg,3,2);
print "\n";
$id = hex(substr($msg,3,2));
print "ID:".$id."\n";
$valLow = hex(substr($msg,5,2));
print "vL:".$valLow."\n";
$valHigh = hex(substr($msg,7,2));
print "vH:".$valHigh."\n";
$valBat = hex(substr($msg,9,2));
if (int($valBat) <= 100) {
      $bat = "critical";
    } elsif (int($valBat) <= 200) {
      $bat = "optimal";
	} else {
      $bat = "ok";
	}
print "Bat:".$bat."\n";
print (($valHigh<<8) + $valLow);

print "Hash\n";
my $selector = "4";
my %modstr = (4,"Light",6,"Water");
print "$modstr{$selector}\n";