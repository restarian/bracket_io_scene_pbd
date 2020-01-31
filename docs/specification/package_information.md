# Bracket Io Scene Pbd
### Package Specifications

----

### Bracket IO Scene PBD help pages
* [Synopsis](https://github.com/restarian/bracket_io_scene_pbd/blob/master/docs/synopsis.md)
* Specification
  * [License information](https://github.com/restarian/bracket_io_scene_pbd/blob/master/docs/specification/license_information.md)
  * **Package information**
----

**Version**: 0.4.0

**Description**: A blender addon which operates a export script for use with the PBD engine

**Author**: [Robert Steckroth](mailto:RobertSteckroth@gmail.com)

**Development dependencies**: [bracket_print](https://npmjs.org/package/bracket_print)

**Optional Dependencies**: [brace_document](https://npmjs.org/package/brace_document) [brace_document_link](https://npmjs.org/package/brace_document_link) [brace_document_mocha](https://npmjs.org/package/brace_document_mocha) [brace_document_navlink](https://npmjs.org/package/brace_document_navlink) [brace_document_specification](https://npmjs.org/package/brace_document_specification)

**Package scripts**:

| Name | Action |
| ---- | ------ |
 | test | ```mocha``` |
 | equateVersion | ```equateVersion``` |
 | make_docs | ```brace_document --navlink --link --link-dest ../Readme.md --link-path ../docs/synopsis.md -r -i docs --force-title --title "Bracket IO Scene PBD help pages" --sort depth --specification``` |

**Keywords**: *markdown*, *documentation*, *platform*, *generation*

**Technologies used in development**:
  * [VIM](https://www.vim.org) As the primary IDE
  * [Windows 10](https://www.microsoft.com/en-us/software-download/windows10) As the development operating environment
  * [Git](https://git-scm.com) For repository management
  * [Github](https://github.com) For repository storage
  * [NPM](https://npmjs.org) For module storage