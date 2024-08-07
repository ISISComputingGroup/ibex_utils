OPI = """<?xml version="1.0" encoding="UTF-8"?>
<display typeId="org.csstudio.opibuilder.Display" version="1.0">
  <show_close_button>true</show_close_button>
  <rules />
  <wuid>46963b75:15b0ef684e0:-7fff</wuid>
  <show_grid>true</show_grid>
  <auto_zoom_to_fit_all>false</auto_zoom_to_fit_all>
  <scripts />
  <height>600</height>
  <macros>
    <include_parent_macros>true</include_parent_macros>
    <PV_ROOT>$(P)</PV_ROOT>
  </macros>
  <boy_version>3.1.4.201301231545</boy_version>
  <show_edit_range>true</show_edit_range>
  <widget_type>Display</widget_type>
  <auto_scale_widgets>
    <auto_scale_widgets>false</auto_scale_widgets>
    <min_width>-1</min_width>
    <min_height>-1</min_height>
  </auto_scale_widgets>
  <background_color>
    <color red="240" green="240" blue="240" />
  </background_color>
  <width>800</width>
  <x>-1</x>
  <name></name>
  <grid_space>6</grid_space>
  <show_ruler>true</show_ruler>
  <y>-1</y>
  <snap_to_geometry>true</snap_to_geometry>
  <foreground_color>
    <color red="192" green="192" blue="192" />
  </foreground_color>
  <actions hook="false" hook_all="false" />
  <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
    <border_style>0</border_style>
    <tooltip></tooltip>
    <horizontal_alignment>0</horizontal_alignment>
    <rules />
    <enabled>true</enabled>
    <wuid>46963b75:15b0ef684e0:-7ee2</wuid>
    <transparent>false</transparent>
    <auto_size>false</auto_size>
    <text>Open a PV</text>
    <scripts />
    <height>37</height>
    <border_width>1</border_width>
    <scale_options>
      <width_scalable>true</width_scalable>
      <height_scalable>true</height_scalable>
      <keep_wh_ratio>false</keep_wh_ratio>
    </scale_options>
    <visible>true</visible>
    <vertical_alignment>1</vertical_alignment>
    <border_color>
      <color name="ISIS_Border" red="0" green="0" blue="0" />
    </border_color>
    <widget_type>Label</widget_type>
    <wrap_words>true</wrap_words>
    <background_color>
      <color name="ISIS_Title_Background_NEW" red="240" green="240" blue="240" />
    </background_color>
    <width>775</width>
    <x>12</x>
    <name>Label_1</name>
    <y>6</y>
    <foreground_color>
      <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
    </foreground_color>
    <actions hook="false" hook_all="false" />
    <show_scrollbar>false</show_scrollbar>
    <font>
      <opifont.name fontName="Segoe UI" height="18" style="1">ISIS_Header1_NEW</opifont.name>
    </font>
  </widget>
  <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
    <border_style>0</border_style>
    <tooltip></tooltip>
    <horizontal_alignment>0</horizontal_alignment>
    <rules />
    <enabled>true</enabled>
    <wuid>46963b75:15b0ef684e0:-7ee1</wuid>
    <transparent>false</transparent>
    <auto_size>false</auto_size>
    <text>$(NAME)</text>
    <scripts />
    <height>37</height>
    <border_width>1</border_width>
    <scale_options>
      <width_scalable>true</width_scalable>
      <height_scalable>true</height_scalable>
      <keep_wh_ratio>false</keep_wh_ratio>
    </scale_options>
    <visible>true</visible>
    <vertical_alignment>1</vertical_alignment>
    <border_color>
      <color name="ISIS_Border" red="0" green="0" blue="0" />
    </border_color>
    <widget_type>Label</widget_type>
    <wrap_words>true</wrap_words>
    <background_color>
      <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
    </background_color>
    <width>775</width>
    <x>12</x>
    <name>Label_2</name>
    <y>42</y>
    <foreground_color>
      <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
    </foreground_color>
    <actions hook="false" hook_all="false" />
    <show_scrollbar>false</show_scrollbar>
    <font>
      <opifont.name fontName="Segoe UI" height="14" style="1">ISIS_Header2_NEW</opifont.name>
    </font>
  </widget>
  <widget typeId="org.csstudio.opibuilder.widgets.groupingContainer" version="1.0">
    <border_style>13</border_style>
    <tooltip></tooltip>
    <rules />
    <enabled>true</enabled>
    <wuid>46963b75:15b0ef684e0:-7ddb</wuid>
    <transparent>false</transparent>
    <lock_children>false</lock_children>
    <scripts />
    <height>157</height>
    <border_width>1</border_width>
    <scale_options>
      <width_scalable>true</width_scalable>
      <height_scalable>true</height_scalable>
      <keep_wh_ratio>false</keep_wh_ratio>
    </scale_options>
    <macros>
      <include_parent_macros>true</include_parent_macros>
    </macros>
    <visible>true</visible>
    <border_color>
      <color name="ISIS_GroupBox_Border_NEW" red="0" green="128" blue="255" />
    </border_color>
    <widget_type>Grouping Container</widget_type>
    <background_color>
      <color name="ISIS_OPI_Background" red="240" green="240" blue="240" />
    </background_color>
    <width>343</width>
    <x>12</x>
    <name>PVs on a Device</name>
    <y>90</y>
    <foreground_color>
      <color name="ISIS_OPI_Foreground" red="192" green="192" blue="192" />
    </foreground_color>
    <actions hook="false" hook_all="false" />
    <show_scrollbar>true</show_scrollbar>
    <font>
      <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_GroupBox_NEW</opifont.name>
    </font>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7f0b</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(DEVPV1)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label</name>
      <y>42</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
      <border_style>0</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7f0a</wuid>
      <transparent>true</transparent>
      <pv_value />
      <auto_size>false</auto_size>
      <text>######</text>
      <rotation_angle>0.0</rotation_angle>
      <scripts />
      <border_alarm_sensitive>true</border_alarm_sensitive>
      <show_units>true</show_units>
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <pv_name>$(PV_ROOT)$(DEVICE)$(DEVPV1)</pv_name>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Update</widget_type>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <wrap_words>false</wrap_words>
      <format_type>0</format_type>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>85</width>
      <x>120</x>
      <name>Text Update</name>
      <y>42</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextInput" version="1.0">
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <pv_value />
      <auto_size>false</auto_size>
      <text>0.0</text>
      <rotation_angle>0.0</rotation_angle>
      <show_units>true</show_units>
      <height>20</height>
      <multiline_input>false</multiline_input>
      <border_width>1</border_width>
      <visible>true</visible>
      <pv_name>$(PV_ROOT)$(DEVICE)$(DEVPV1):SP</pv_name>
      <selector_type>0</selector_type>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Input</widget_type>
      <confirm_message></confirm_message>
      <name>Text Input</name>
      <actions hook="false" hook_all="false" />
      <border_style>3</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7f09</wuid>
      <transparent>false</transparent>
      <scripts />
      <border_alarm_sensitive>false</border_alarm_sensitive>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <vertical_alignment>1</vertical_alignment>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <format_type>0</format_type>
      <limits_from_pv>false</limits_from_pv>
      <background_color>
        <color name="ISIS_Textbox_Background" red="255" green="255" blue="255" />
      </background_color>
      <width>90</width>
      <x>216</x>
      <y>42</y>
      <maximum>1.7976931348623157E308</maximum>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <minimum>-1.7976931348623157E308</minimum>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d8f</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(DEVPV2)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label_1</name>
      <y>72</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
      <border_style>0</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d8e</wuid>
      <transparent>true</transparent>
      <pv_value />
      <auto_size>false</auto_size>
      <text>######</text>
      <rotation_angle>0.0</rotation_angle>
      <scripts />
      <border_alarm_sensitive>true</border_alarm_sensitive>
      <show_units>true</show_units>
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <pv_name>$(PV_ROOT)$(DEVICE)$(DEVPV2)</pv_name>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Update</widget_type>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <wrap_words>false</wrap_words>
      <format_type>0</format_type>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>85</width>
      <x>120</x>
      <name>Text Update_1</name>
      <y>72</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextInput" version="1.0">
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <pv_value />
      <auto_size>false</auto_size>
      <text>0.0</text>
      <rotation_angle>0.0</rotation_angle>
      <show_units>true</show_units>
      <height>20</height>
      <multiline_input>false</multiline_input>
      <border_width>1</border_width>
      <visible>true</visible>
      <pv_name>$(PV_ROOT)$(DEVICE)$(DEVPV2):SP</pv_name>
      <selector_type>0</selector_type>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Input</widget_type>
      <confirm_message></confirm_message>
      <name>Text Input_1</name>
      <actions hook="false" hook_all="false" />
      <border_style>3</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d8d</wuid>
      <transparent>false</transparent>
      <scripts />
      <border_alarm_sensitive>false</border_alarm_sensitive>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <vertical_alignment>1</vertical_alignment>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <format_type>0</format_type>
      <limits_from_pv>false</limits_from_pv>
      <background_color>
        <color name="ISIS_Textbox_Background" red="255" green="255" blue="255" />
      </background_color>
      <width>90</width>
      <x>216</x>
      <y>72</y>
      <maximum>1.7976931348623157E308</maximum>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <minimum>-1.7976931348623157E308</minimum>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d87</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(DEVPV3)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label_2</name>
      <y>102</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
      <border_style>0</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d86</wuid>
      <transparent>true</transparent>
      <pv_value />
      <auto_size>false</auto_size>
      <text>######</text>
      <rotation_angle>0.0</rotation_angle>
      <scripts />
      <border_alarm_sensitive>true</border_alarm_sensitive>
      <show_units>true</show_units>
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <pv_name>$(PV_ROOT)$(DEVICE)$(DEVPV3)</pv_name>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Update</widget_type>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <wrap_words>false</wrap_words>
      <format_type>0</format_type>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>85</width>
      <x>120</x>
      <name>Text Update_2</name>
      <y>102</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextInput" version="1.0">
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <pv_value />
      <auto_size>false</auto_size>
      <text>0.0</text>
      <rotation_angle>0.0</rotation_angle>
      <show_units>true</show_units>
      <height>20</height>
      <multiline_input>false</multiline_input>
      <border_width>1</border_width>
      <visible>true</visible>
      <pv_name>$(PV_ROOT)$(DEVICE)$(DEVPV3):SP</pv_name>
      <selector_type>0</selector_type>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Input</widget_type>
      <confirm_message></confirm_message>
      <name>Text Input_2</name>
      <actions hook="false" hook_all="false" />
      <border_style>3</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d85</wuid>
      <transparent>false</transparent>
      <scripts />
      <border_alarm_sensitive>false</border_alarm_sensitive>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <vertical_alignment>1</vertical_alignment>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <format_type>0</format_type>
      <limits_from_pv>false</limits_from_pv>
      <background_color>
        <color name="ISIS_Textbox_Background" red="255" green="255" blue="255" />
      </background_color>
      <width>90</width>
      <x>216</x>
      <y>102</y>
      <maximum>1.7976931348623157E308</maximum>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <minimum>-1.7976931348623157E308</minimum>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d19</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>Device PV Stem</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label_3</name>
      <y>6</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7d13</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(PV_ROOT)$(DEVICE)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>197</width>
      <x>109</x>
      <name>Label_4</name>
      <y>6</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
  </widget>
  <widget typeId="org.csstudio.opibuilder.widgets.groupingContainer" version="1.0">
    <border_style>13</border_style>
    <tooltip></tooltip>
    <rules />
    <enabled>true</enabled>
    <wuid>46963b75:15b0ef684e0:-7cee</wuid>
    <transparent>false</transparent>
    <lock_children>false</lock_children>
    <scripts />
    <height>121</height>
    <border_width>1</border_width>
    <scale_options>
      <width_scalable>true</width_scalable>
      <height_scalable>true</height_scalable>
      <keep_wh_ratio>false</keep_wh_ratio>
    </scale_options>
    <macros>
      <include_parent_macros>true</include_parent_macros>
    </macros>
    <visible>true</visible>
    <border_color>
      <color name="ISIS_GroupBox_Border_NEW" red="0" green="128" blue="255" />
    </border_color>
    <widget_type>Grouping Container</widget_type>
    <background_color>
      <color name="ISIS_OPI_Background" red="240" green="240" blue="240" />
    </background_color>
    <width>343</width>
    <x>12</x>
    <name>General PVs</name>
    <y>258</y>
    <foreground_color>
      <color name="ISIS_OPI_Foreground" red="192" green="192" blue="192" />
    </foreground_color>
    <actions hook="false" hook_all="false" />
    <show_scrollbar>true</show_scrollbar>
    <font>
      <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_GroupBox_NEW</opifont.name>
    </font>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7f0b</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(GENPV1)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label</name>
      <y>6</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
      <border_style>0</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7f0a</wuid>
      <transparent>true</transparent>
      <pv_value />
      <auto_size>false</auto_size>
      <text>######</text>
      <rotation_angle>0.0</rotation_angle>
      <scripts />
      <border_alarm_sensitive>true</border_alarm_sensitive>
      <show_units>true</show_units>
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <pv_name>$(GENPV1)</pv_name>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Update</widget_type>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <wrap_words>false</wrap_words>
      <format_type>0</format_type>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>85</width>
      <x>120</x>
      <name>Text Update</name>
      <y>6</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextInput" version="1.0">
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <pv_value />
      <auto_size>false</auto_size>
      <text>0.0</text>
      <rotation_angle>0.0</rotation_angle>
      <show_units>true</show_units>
      <height>20</height>
      <multiline_input>false</multiline_input>
      <border_width>1</border_width>
      <visible>true</visible>
      <pv_name>$(GENPV1):SP</pv_name>
      <selector_type>0</selector_type>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Input</widget_type>
      <confirm_message></confirm_message>
      <name>Text Input</name>
      <actions hook="false" hook_all="false" />
      <border_style>3</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7f09</wuid>
      <transparent>false</transparent>
      <scripts />
      <border_alarm_sensitive>false</border_alarm_sensitive>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <vertical_alignment>1</vertical_alignment>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <format_type>0</format_type>
      <limits_from_pv>false</limits_from_pv>
      <background_color>
        <color name="ISIS_Textbox_Background" red="255" green="255" blue="255" />
      </background_color>
      <width>90</width>
      <x>216</x>
      <y>6</y>
      <maximum>1.7976931348623157E308</maximum>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <minimum>-1.7976931348623157E308</minimum>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7bfe</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(GENPV2)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label_1</name>
      <y>36</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
      <border_style>0</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7bfd</wuid>
      <transparent>true</transparent>
      <pv_value />
      <auto_size>false</auto_size>
      <text>######</text>
      <rotation_angle>0.0</rotation_angle>
      <scripts />
      <border_alarm_sensitive>true</border_alarm_sensitive>
      <show_units>true</show_units>
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <pv_name>$(GENPV2)</pv_name>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Update</widget_type>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <wrap_words>false</wrap_words>
      <format_type>0</format_type>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>85</width>
      <x>120</x>
      <name>Text Update_1</name>
      <y>36</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextInput" version="1.0">
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <pv_value />
      <auto_size>false</auto_size>
      <text>0.0</text>
      <rotation_angle>0.0</rotation_angle>
      <show_units>true</show_units>
      <height>20</height>
      <multiline_input>false</multiline_input>
      <border_width>1</border_width>
      <visible>true</visible>
      <pv_name>$(GENPV2):SP</pv_name>
      <selector_type>0</selector_type>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Input</widget_type>
      <confirm_message></confirm_message>
      <name>Text Input_1</name>
      <actions hook="false" hook_all="false" />
      <border_style>3</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7bfc</wuid>
      <transparent>false</transparent>
      <scripts />
      <border_alarm_sensitive>false</border_alarm_sensitive>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <vertical_alignment>1</vertical_alignment>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <format_type>0</format_type>
      <limits_from_pv>false</limits_from_pv>
      <background_color>
        <color name="ISIS_Textbox_Background" red="255" green="255" blue="255" />
      </background_color>
      <width>90</width>
      <x>216</x>
      <y>36</y>
      <maximum>1.7976931348623157E308</maximum>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <minimum>-1.7976931348623157E308</minimum>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.Label" version="1.0">
      <border_style>0</border_style>
      <tooltip></tooltip>
      <horizontal_alignment>2</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7bf6</wuid>
      <transparent>false</transparent>
      <auto_size>false</auto_size>
      <text>$(GENPV3)</text>
      <scripts />
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <widget_type>Label</widget_type>
      <wrap_words>true</wrap_words>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>96</width>
      <x>6</x>
      <name>Label_2</name>
      <y>66</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <show_scrollbar>false</show_scrollbar>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="1">ISIS_Label_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
      <border_style>0</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7bf5</wuid>
      <transparent>true</transparent>
      <pv_value />
      <auto_size>false</auto_size>
      <text>######</text>
      <rotation_angle>0.0</rotation_angle>
      <scripts />
      <border_alarm_sensitive>true</border_alarm_sensitive>
      <show_units>true</show_units>
      <height>20</height>
      <border_width>1</border_width>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <visible>true</visible>
      <pv_name>$(GENPV3)</pv_name>
      <vertical_alignment>1</vertical_alignment>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Update</widget_type>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <wrap_words>false</wrap_words>
      <format_type>0</format_type>
      <background_color>
        <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
      </background_color>
      <width>85</width>
      <x>120</x>
      <name>Text Update_2</name>
      <y>66</y>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <actions hook="false" hook_all="false" />
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
    <widget typeId="org.csstudio.opibuilder.widgets.TextInput" version="1.0">
      <precision>0</precision>
      <tooltip>$(pv_name)
$(pv_value)</tooltip>
      <horizontal_alignment>0</horizontal_alignment>
      <rules />
      <pv_value />
      <auto_size>false</auto_size>
      <text>0.0</text>
      <rotation_angle>0.0</rotation_angle>
      <show_units>true</show_units>
      <height>20</height>
      <multiline_input>false</multiline_input>
      <border_width>1</border_width>
      <visible>true</visible>
      <pv_name>$(GENPV3):SP</pv_name>
      <selector_type>0</selector_type>
      <border_color>
        <color name="ISIS_Border" red="0" green="0" blue="0" />
      </border_color>
      <precision_from_pv>true</precision_from_pv>
      <widget_type>Text Input</widget_type>
      <confirm_message></confirm_message>
      <name>Text Input_2</name>
      <actions hook="false" hook_all="false" />
      <border_style>3</border_style>
      <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
      <enabled>true</enabled>
      <wuid>46963b75:15b0ef684e0:-7bf4</wuid>
      <transparent>false</transparent>
      <scripts />
      <border_alarm_sensitive>false</border_alarm_sensitive>
      <scale_options>
        <width_scalable>true</width_scalable>
        <height_scalable>true</height_scalable>
        <keep_wh_ratio>false</keep_wh_ratio>
      </scale_options>
      <vertical_alignment>1</vertical_alignment>
      <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
      <format_type>0</format_type>
      <limits_from_pv>false</limits_from_pv>
      <background_color>
        <color name="ISIS_Textbox_Background" red="255" green="255" blue="255" />
      </background_color>
      <width>90</width>
      <x>216</x>
      <y>66</y>
      <maximum>1.7976931348623157E308</maximum>
      <foreground_color>
        <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
      </foreground_color>
      <minimum>-1.7976931348623157E308</minimum>
      <font>
        <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
      </font>
    </widget>
  </widget>
  {WIDGET}
</display>
"""


WIDGET = """
  <widget typeId="org.csstudio.opibuilder.widgets.TextUpdate" version="1.0">
    <border_style>0</border_style>
    <forecolor_alarm_sensitive>false</forecolor_alarm_sensitive>
    <precision>0</precision>
    <tooltip>$(pv_name)
$(pv_value)</tooltip>
    <horizontal_alignment>0</horizontal_alignment>
    <rules />
    <enabled>true</enabled>
    <wuid>-29f19740:15b1a0df5a7:-7fcb</wuid>
    <transparent>true</transparent>
    <pv_value />
    <auto_size>false</auto_size>
    <text>######</text>
    <rotation_angle>0.0</rotation_angle>
    <scripts />
    <border_alarm_sensitive>true</border_alarm_sensitive>
    <show_units>true</show_units>
    <height>20</height>
    <border_width>1</border_width>
    <scale_options>
      <width_scalable>true</width_scalable>
      <height_scalable>true</height_scalable>
      <keep_wh_ratio>false</keep_wh_ratio>
    </scale_options>
    <visible>true</visible>
    <pv_name>$(PV_ROOT)SIMPLE:NUMBERED{NUMBER}</pv_name>
    <vertical_alignment>1</vertical_alignment>
    <border_color>
      <color name="ISIS_Border" red="0" green="0" blue="0" />
    </border_color>
    <precision_from_pv>true</precision_from_pv>
    <widget_type>Text Update</widget_type>
    <backcolor_alarm_sensitive>false</backcolor_alarm_sensitive>
    <wrap_words>false</wrap_words>
    <format_type>0</format_type>
    <background_color>
      <color name="ISIS_Label_Background" red="240" green="240" blue="240" />
    </background_color>
    <width>85</width>
    <x>48</x>
    <name>Text Update_2</name>
    <y>{Y}</y>
    <foreground_color>
      <color name="ISIS_Standard_Text" red="0" green="0" blue="0" />
    </foreground_color>
    <actions hook="false" hook_all="false" />
    <font>
      <opifont.name fontName="Segoe UI" height="9" style="0">ISIS_Value_NEW</opifont.name>
    </font>
  </widget>
"""


NUMBER_OF_PVS = 1000

widgets = ""
initially = 408
for number in range(1, NUMBER_OF_PVS + 1):
    widget_y = initially + 20 * number
    widgets += WIDGET.format(Y=widget_y, NUMBER=number)

with open(
    r"C:\Instrument\Dev\ibex_gui\base\uk.ac.stfc.isis.ibex.opis\resources\OpenPVs.opi", mode="w"
) as f:
    f.write(OPI.format(WIDGET=widgets))
