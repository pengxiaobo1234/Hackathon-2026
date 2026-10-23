package main

import ("testing"; "math")
func fresh() { Best=0; Seed=20261023; StartRun(); Invincible=0; SpawnTime=1000; PowerTime=1000 }
func advance(seconds float64) { for i:=0;i<int(seconds*120);i++ {Tick(1.0/120)} }
func obstacle(kind int, x float64){ObActive[0]=true;ObKind[0]=kind;ObX[0]=x}
func TestStartAndRestart(t *testing.T){fresh();Coins=7;Distance=30;Best=650;Mode=3;StartRun();if Mode!=1||Coins!=0||Distance!=0||Lives!=3||Best!=650{t.Fatal("restart state",Mode,Coins,Distance,Lives,Best)}}
func TestDoubleJumpAndLanding(t *testing.T){fresh();JumpAction();advance(.2);first:=Height;JumpAction();v:=JumpVelocity;JumpAction();if Jumps!=2||JumpVelocity!=v{t.Fatal("third jump accepted")};advance(.2);if Height<=first{t.Fatal("double jump did not gain height")};advance(2);if Height!=0||Jumps!=0{t.Fatal("landing did not reset",Height,Jumps)}}
func TestJumpClearance(t *testing.T){fresh();JumpAction();peak:=0.0;for i:=0;i<120;i++{Tick(1.0/120);peak=math.Max(peak,Height)};if peak<105||peak>115{t.Fatal("unexpected jump clearance",peak)}}
func TestPauseFreezesWorld(t *testing.T){fresh();JumpAction();advance(.1);PauseAction();h,d,c,v:=Height,Distance,Clock,JumpVelocity;advance(2);JumpAction();SlideAction();if Height!=h||Distance!=d||Clock!=c||JumpVelocity!=v{t.Fatal("pause advanced simulation")};PauseAction();advance(.1);if Clock<=c{t.Fatal("resume did not advance")}}
func TestSlideExpires(t *testing.T){fresh();SlideAction();if SlideTime<=0{t.Fatal("slide failed")};advance(1);if SlideTime!=0{t.Fatal("slide did not expire")}}
func TestFastFall(t *testing.T){fresh();JumpAction();advance(.2);SlideAction();if JumpVelocity!=-750{t.Fatal("fast fall failed")};advance(.3);if Height!=0{t.Fatal("fast fall did not land")}}
func TestLowObstacleHits(t *testing.T){fresh();obstacle(0,-280);Tick(1.0/120);if Lives!=2{t.Fatal("crate did not hit")}}
func TestJumpAvoidsObstacle(t *testing.T){fresh();Height=80;Jumps=1;obstacle(0,-280);Tick(1.0/120);if Lives!=3{t.Fatal("jump hit crate")}}
func TestDroneRequiresSlide(t *testing.T){fresh();obstacle(2,-280);Tick(1.0/120);if Lives!=2{t.Fatal("standing passed drone")};fresh();SlideAction();obstacle(2,-280);Tick(1.0/120);if Lives!=3{t.Fatal("slide hit drone")}}
func TestTallWallNeedsClearance(t *testing.T){fresh();Height=70;obstacle(1,-280);Tick(1.0/120);if Lives!=2{t.Fatal("low jump passed tall wall")};fresh();Height=145;obstacle(1,-280);Tick(1.0/120);if Lives!=3{t.Fatal("high jump hit wall")}}
func TestInvulnerability(t *testing.T){fresh();Hit();Hit();Hit();if Lives!=2{t.Fatal("multiple damage in immunity window")};advance(2);Hit();if Lives!=1{t.Fatal("immunity never expired")}}
func TestShieldAbsorbsOneHit(t *testing.T){fresh();ShieldTime=9;Hit();if Lives!=3||ShieldTime!=0{t.Fatal("shield failed")};advance(1.1);Hit();if Lives!=2{t.Fatal("second hit did not consume life")}}
func TestPitRescue(t *testing.T){fresh();obstacle(3,-210);advance(.8);if Lives!=2||Height<0||!(!ObActive[0]){t.Fatal("pit rescue failed",Lives,Height,ObActive[0])}}
func TestCoinAndMagnet(t *testing.T){fresh();AddCoin(-280,38);Tick(1.0/120);if Coins!=1||CoinActive[0]{t.Fatal("coin pickup failed")};fresh();MagnetTime=9;AddCoin(-100,170);advance(.6);if Coins!=1{t.Fatal("magnet failed",CoinX[0],CoinY[0])}}
func TestPowerPickups(t *testing.T){for k:=0;k<2;k++{fresh();PowerActive=true;PowerKind=k;PowerX=-280;PowerY=60;Tick(1.0/120);if PowerActive{t.Fatal("power not picked")};if k==0&&ShieldTime<=8.9{t.Fatal("shield not activated")};if k==1&&MagnetTime<=8.9{t.Fatal("magnet not activated")}}}
func TestScoreAndGameOver(t *testing.T){fresh();Coins=4;Distance=50;Tick(1.0/120);if Score!=700||Best!=700{t.Fatal("score formula",Score,Best)};Lives=1;Hit();if Mode!=3||Best!=Score{t.Fatal("gameover")};d:=Distance;Tick(.05);if Distance!=d{t.Fatal("gameover kept running")}}
func TestFrameClampAndSpeed(t *testing.T){fresh();Tick(10);if Clock>.050001{t.Fatal("frame clamp failed")};Clock=200;Tick(.01);if Speed!=480{t.Fatal("speed cap")};d:=Distance;Tick(-1);if Distance!=d{t.Fatal("negative dt accepted")}}
func TestDeterministicSpawns(t *testing.T){fresh();SpawnTime=0;Tick(.01);if !ObActive[0]||!(ObKind[0]==0||ObKind[0]==2){t.Fatal("tutorial obstacle")};if CoinActive[0]!=true||CoinActive[4]!=true{t.Fatal("coin trail")};seen:=[4]bool{};for j:=0;j<500;j++{Clock=60;for i:=0;i<4;i++{ObActive[i]=false};SpawnObstacle();seen[ObKind[0]]=true};for k,v:=range seen{if !v{t.Fatal("missing obstacle kind",k)}}}
func TestLongRunFiniteState(t *testing.T){fresh();SpawnTime=0;PowerTime=0;for i:=0;i<120*180;i++{Invincible=10;if Height<0 {JumpAction()};if i%70==0{JumpAction()};Tick(1.0/120);if math.IsNaN(Height)||math.IsNaN(Distance)||math.IsInf(Height,0){t.Fatal("invalid state")};if Mode==3{StartRun()}};if Score<0||Speed>480{t.Fatal("bad long-run state")}}
