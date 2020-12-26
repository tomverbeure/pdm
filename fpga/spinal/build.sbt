/*
name := "SpinalTemplateSbt"

version := "1.0"

scalaVersion := "2.11.12"

EclipseKeys.withSource := true

libraryDependencies ++= Seq(
  "com.github.spinalhdl" % "spinalhdl-core_2.11" % "1.3.5",
  "com.github.spinalhdl" % "spinalhdl-lib_2.11" % "1.3.5"
)

fork := true
*/

lazy val root = (project in file(".")).
  settings(
    inThisBuild(List(
      organization := "com.github.spinalhdl",
      scalaVersion := "2.11.12",
      version      := "1.0.0"
    )),
    libraryDependencies ++= Seq(
      "com.github.spinalhdl" % "spinalhdl-core_2.11" % "1.3.8",
      "com.github.spinalhdl" % "spinalhdl-lib_2.11"  % "1.3.8",
      "org.scalatest" % "scalatest_2.11" % "2.2.1",
      "org.yaml" % "snakeyaml" % "1.8"
    ),
    name := "pdm_test"
).dependsOn(vexRiscv)

lazy val vexRiscv = RootProject(file("../VexRiscv.local"))

fork := true
