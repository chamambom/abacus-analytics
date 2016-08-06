Bootstrap remote data plugin
=====================
Author: Stephen Hoogendijk - TheCodeAssassin

This project is licensed under the GPLV2 license.

This plugin uses the jQuery loadmask plugin by Sergiy Kovalchuk.

================================================

Simple boostrap plugin to allow tabs and accordions to fetch their data from a remote source

*The script is only 2.5k compressed!*

Requirements
============

* Bootstrap 2.3 or higher

Installation
============

- Clone this repository or download the latest stable
- Copy the bootstrap-remote-tabs.js in your js directory.
- Include it:
<script type="text/javascript" src="js/bootstrap-remote-tabs-2-3.js"></script>
- If you want a loading mask to appear when you load your remote content, also include the following files: js/jquery.loadmask.js (before the remote tabs plugin)
,css/jquery.loadmask.css. and img/loading.gif.


Usage
=====
You can use the following properties to enable remote data tabs:


|   Property   |   Value    |   Effect  | Required |
|--------------|-------------| ------------|------------ |
|data-tab-url  | url |  The remote data url  | True |
|data-tab-always-refresh | true |  Always refresh this tab | False |
|data-tab-callback | function-name | Callback to be fired upon show (will be executed after the data is loaded). It takes the following arguments: html, trigger, container, (optional) json data that was sent | False |
|data-tab-json | json | JSON data to be send when fetching the URL | False |
|data-tab-delay | number |  Simulate a delay (in miliseconds) | False |

Check the demo for details on how to use this plugin.

*Note: The properties are still named data-tab due to backwards compatibility*

Settings
===
You can change the default settings of this plugin by providing the settings as a global variable.

There are two options currently:

* customLoadFn (callback): this is a custom loading function, defaults to the built-in loader
* loadFirstTab (boolean): whether to load the first tab on page load or not (defaults to false)

```
var bootstrapRemoteTabSettings = {
   customLoadFn: function(isLoading) {
      var loader = $('.custom-loader');
      
      if (isLoading) {
        loader.show();
      } else {
        loader.hide();
      }
   },
   loadFirstTab: true
}
```

Note
====
This plugin hooks into the bootstrap tab/accordion 'show' event. In order to use a custom event callback, you can provide data-tab-callback
to let the plugin execute your custom callback. If you want a callback to be fired after the show event, use the native
shown event.

Changelog
===

Version 1.2.1
------
*  Fixed issue #7 - reported by tofanelli


Version 1.2.0
------
*  Added settings
*  Added load first page option (default false)
*  Added option to have a custom loading function


Version 1.1.1
------
*  Added support for accordions


Version 1.1.0
------
*  Added feature to go to the tab specified in the URL (for example #tab1 will open the tab with ID #tab1)


Version 1.0.1
------
*   Added minified version of the script. Fixed small issue with gracefully degrading

Version 1.0.0
------
*   Initial release

