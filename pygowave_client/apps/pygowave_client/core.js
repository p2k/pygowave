/*
 * PyGoWave Client
 * Copyright (C) 2010 Patrick "p2k" Schneider
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

/** @namespace

  This collection of JavaScript libraries represent the PyGoWave Client
  interface for web browsers. It communicates seamlessly with any PyGoWave
  Server instance.
  
  @extends SC.Object
*/
PyGoWaveClient = SC.Application.create(
  /** @scope PyGoWaveClient.prototype */ {

  NAMESPACE: 'PyGoWaveClient',
  VERSION: '0.2.0',

  // This is your application store.  You will use this store to access all
  // of your model data.  You can also set a data source on this store to
  // connect to a backend server.  The default setup below connects the store
  // to any fixtures you define.
  store: SC.Store.create().from(SC.Record.fixtures)
  
  // TODO: Add global constants or singleton objects needed by your app here.

}) ;
