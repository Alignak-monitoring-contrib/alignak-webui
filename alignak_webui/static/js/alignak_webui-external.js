/*
 * Copyright (c) 2015-2017:
 *   Frederic Mohier, frederic.mohier@alignak.net
 *
 * This file is part of (WebUI).
 *
 * (WebUI) is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * (WebUI) is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * Global variables for host/service states
 */
var g_hosts_states = {
   'up': {
      'color': '#27ae60',
      'background': '#669999',
      'label': 'Up'
   },
   'unreachable': {
      'color': '#9b59b6',
      'background': '#669999',
      'label': 'Unreachable'
   },
   'down': {
      'color': '#e74c3c',
      'background': '#669999',
      'label': 'Down'
   },
   'unknown': {
      'color': '#2980b9',
      'background': '#669999',
      'label': 'Unknown'
   },
   'acknowledged': {
      'color': '#f39c12',
      'background': '#669999',
      'label': 'Acknowledged'
   },
   'in_downtime': {
      'color': '#f1c40f',
      'background': '#669999',
      'label': 'Downtime'
   }
};
var g_services_states = {
   'ok': {
      'color': '#27ae60',
      'background': '#669999',
      'label': 'Ok'
   },
   'warning': {
      'color': '#e67e22',
      'background': '#669999',
      'label': 'Warning'
   },
   'critical': {
      'color': '#e74c3c',
      'background': '#669999',
      'label': 'Critical'
   },
   'unknown': {
      'color': '#2980b9',
      'background': '#669999',
      'label': 'Unknown'
   },
   'unreachable': {
      'color': '#9b59b6',
      'background': '#669999',
      'label': 'Unreachable'
   },
   'acknowledged': {
      'color': '#f39c12',
      'background': '#669999',
      'label': 'Acknowledged'
   },
   'in_downtime': {
      'color': '#f1c40f',
      'background': '#669999',
      'label': 'Downtime'
   }
};
var g_hoverBackgroundColor = "#669999";
var g_hoverBorderColor = "#669999";
