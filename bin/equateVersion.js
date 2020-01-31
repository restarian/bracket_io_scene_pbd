#! /usr/bin/env node

var fs = require("fs"),
	path = require("path"),
	Print = require("bracket_print")

var up = Print({level: 1, log_title: "bin/"+path.basename(__filename), title_stamp: false})

var up_err = up.spawn({level: 2})


fs.readFile("__init__.py", function(error, stdout) {

	if ( error )
		up_err.log_true(error) && process.exit(7)

	var py_version = (stdout.toString().match(/[\",\']version[\",\;]:\s*\(([^\)]+)\)/i)||[""])[1]
	if ( !/\S/.test(py_version) ) 
		up_err.log_true("The version could not be extracted fromm the __init__.py file.") && process.exit(9)

	py_version = py_version.replace(/ /g, "").replace(/\,/g, ".")
	package_path = path.join("..", "package.json")
	var package = require(package_path)

	if ( typeof package !== "object" && package !== null ) {
		up.log_undefined("The package.json file could not be loaded (or there is one present). A package.json file will be created.")
		package = {version: ""}
	}


	package.version = py_version
	fs.writeFile(path.join(__dirname, "..", "package.json"), up.option({log_title: false, compression: 1, 
	quote_qualifier: true, denote_quoting: "\"", style: false}).toString(package), function(error) {

		if ( error )
			up_err.log_true("Write:", error) && process.exit(7)
		else
			up.log_undefined("Success") && process.exit(0)

	})

})

