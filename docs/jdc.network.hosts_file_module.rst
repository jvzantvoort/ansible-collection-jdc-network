.. Created with antsibull-docs 2.14.0

jdc.network.hosts_file module -- Manage the hosts file
++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module is part of the `jdc.network collection <https://galaxy.ansible.com/ui/repo/published/jdc/network/>`_ (version 1.0.0).

It is not included in ``ansible-core``.
To check whether it is installed, run ``ansible-galaxy collection list``.

To install it, use: :code:`ansible-galaxy collection install jdc.network`.

To use it in a playbook, specify: ``jdc.network.hosts_file``.


.. contents::
   :local:
   :depth: 1


Synopsis
--------

- The \ `jdc.network.hosts\_file <hosts_file_module.rst>`__ module helps managing the contents of the :literal:`/etc/hosts` file.








Parameters
----------

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th><p>Parameter</p></th>
    <th><p>Comments</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-debuglog"></div>
      <p style="display: inline;"><strong>debuglog</strong></p>
      <a class="ansibleOptionLink" href="#parameter-debuglog" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>defined log file for debugging</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-defaults"></div>
      <p style="display: inline;"><strong>defaults</strong></p>
      <a class="ansibleOptionLink" href="#parameter-defaults" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>add the default entries</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-definitions"></div>
      <p style="display: inline;"><strong>definitions</strong></p>
      <a class="ansibleOptionLink" href="#parameter-definitions" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>List of dicts</p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-hostsfile"></div>
      <p style="display: inline;"><strong>hostsfile</strong></p>
      <a class="ansibleOptionLink" href="#parameter-hostsfile" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>Define the hosts file</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">&#34;/etc/hosts&#34;</code></p>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="parameter-state"></div>
      <p style="display: inline;"><strong>state</strong></p>
      <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>state choices absent or present</p>
      <p style="margin-top: 8px;"><b style="color: blue;">Default:</b> <code style="color: blue;">&#34;present&#34;</code></p>
    </td>
  </tr>
  </tbody>
  </table>






Examples
--------

.. code-block:: yaml

    - name: add pietje
      jdc.network.hosts_file:
        hostsfile: /tmp/lala
        definitions:
          - ipaddress: 172.0.0.100
            hostnames:
              - pietje
              - lala
              - lala.lala
          - ipaddress: 172.0.0.101
            hostnames:
              - fred

    - name: remove lala
      jdc.network.hosts_file:
        hostsfile: /tmp/lala
        state: absent
        definitions:
          - ipaddress: 172.0.0.100
            hostnames:
              - lala




Return Values
-------------
The following are the fields unique to this module:

.. raw:: html

  <table style="width: 100%;">
  <thead>
    <tr>
    <th><p>Key</p></th>
    <th><p>Description</p></th>
  </tr>
  </thead>
  <tbody>
  <tr>
    <td valign="top">
      <div class="ansibleOptionAnchor" id="return-hostsfile"></div>
      <p style="display: inline;"><strong>hostsfile</strong></p>
      <a class="ansibleOptionLink" href="#return-hostsfile" title="Permalink to this return value"></a>
      <p style="font-size: small; margin-bottom: 0;">
        <span style="color: purple;">string</span>
      </p>
    </td>
    <td valign="top">
      <p>the path to <code class="ansible-option literal notranslate"><strong><a class="reference internal" href="#parameter-/etc/hosts"><span class="std std-ref"><span class="pre">/etc/hosts</span></span></a></strong></code></p>
      <p style="margin-top: 8px;"><b>Returned:</b> always</p>
      <p style="margin-top: 8px; color: blue; word-wrap: break-word; word-break: break-all;"><b style="color: black;">Sample:</b> <code>&#34;/etc/hosts&#34;</code></p>
    </td>
  </tr>
  </tbody>
  </table>




Authors
~~~~~~~

- John van Zantvoort (@jvzantvoort)



Collection links
~~~~~~~~~~~~~~~~

* `Issue Tracker <https://github.com/jvzantvoort/ansible-collection-jdc-network/issues>`__
* `Repository (Sources) <https://github.com/jvzantvoort/ansible-collection-jdc-network>`__
