ST7789VW incorporate the gamma correction function to display 262,244 colors
for the LCD panel. The gamma correction is performed with 3 groups of 
registers, which are gradient adjustment, contrast adjustment and 
fine-adjustment registers for positive and negative polarities, and RGB can
be adjusted individually.

ST7789VW digital gamma function can implement the RGB gamma correction
independently. ST7789VW utilizes look-up table of digital gamma to change ram
data, and then display the changed data from source driver.

There are 2 registers and each register has 64 bytes to set R, G, B gamma
independently. When bit DGMEN be set to 1, R and B gamma will be mapped via
look-up table of digital gamma to gray level voltage. 
#############################################################################

GAMSET    0x26 : Gamma Set
                 System Function Command Table 1.
          0x01 : Gamma Curve 1 (G2.2) 
          0x02 : Gamma Curve 2 (G1.8) 
          0x04 : Gamma Curve 3 (G2.5) 
          0x08 : Gamma Curve 4 (G1.0)
#############################################################################

DGMEN     0xBA : Digital Gamma Enable
                 System Function Command Table 2.

          0x00 : disable digital gamma
          0x04 : enable digital gamma
#############################################################################

PVGAMCTRL 0xE0 : Positive Voltage Gamma Control
                 System Function Command Table 2.
                 Gamma Reference Voltage(Positive) VAP   4.45  6.40 V Note 6 
                 Gamma Reference Voltage(Negative) VAN  -4.6  -2.65 V
                 Note 6. Default register setting of Vcom & Vcomoffset is 0x20

          Parameter Descriptions 
                        D7     D6     D5     D4     D3     D2     D1     D0 
          1st Parm : V63P3  V63P2  V63P1  V63P0   V0P3   V0P2   V0P1   V0P0  
          2nd Parm :     0      0   V1P5   V1P4   V1P3   V1P2   V1P1   V1P0  
          3rd Parm :     0      0   V2P5   V2P4   V2P3   V2P2   V2P1   V2P0  
          4th Parm :     0      0      0   V4P4   V4P3   V4P2   V4P1   V4P0  
          5th Parm :     0      0      0   V6P4   V6P3   V6P2   V6P1   V6P0  
          6th Parm :     0      0   J0P1   J0P0  V13P3  V13P2  V13P1  V13P0  
          7th Parm :     0  V20P6  V20P5  V20P4  V20P3  V20P2  V20P1  V20P0  
          8th Parm :     0  V36P2  V36P1  V36P0      0  V27P2  V27P1  V27P0  
          9th Parm :     0  V43P6  V43P5  V43P4  V43P3  V43P2  V43P1  V43P0  
         10th Parm :     0      0   J1P1   J1P0  V50P3  V50P2  V50P1  V50P0  
         11th Parm :     0      0      0  V57P4  V57P3  V57P2  V57P1  V57P0  
         12th Parm :     0      0      0  V59P4  V59P3  V59P2  V59P1  V59P0  
         13th Parm :     0      0  V61P5  V61P4  V61P3  V61P2  V61P1  V61P0  
         14th Parm :     0      0  V62P5  V62P4  V62P3  V62P2  V62P1  V62P0

         Default Values
          VP0[3:0] : 0x00 
          VP1[5:0] : 0x2C 
          VP2[5:0] : 0x2E 
          VP4[4:0] : 0x15 
          VP6[4:0] : 0x10 
         VP13[3:0] : 0x09 
         VP20[6:0] : 0x48 
         VP27[2:0] : 0x03 
         VP36[2:0] : 0x03 
         VP43[6:0] : 0x53 
         VP50[3:0] : 0x0B 
         VP57[4:0] : 0x19 
         VP59[4:0] : 0x18 
         VP61[5:0] : 0x20 
         VP62[5:0] : 0x25
         VP63[3:0] : 0x07 
          JP0[1:0] : 0x00 
          JP1[1:0] : 0x00          
#############################################################################

NVGAMCTRL 0xE1 : Negative Voltage Gamma Control
                 System Function Command Table 2.

          Parameter Descriptions 
                        D7     D6     D5     D4     D3     D2     D1     D0 
          1st Parm : V63N3  V63N2  V63N1  V63N0   V0N3   V0N2   V0N1   V0N0  
          2nd Parm :     0      0   V1N5   V1N4   V1N3   V1N2   V1N1   V1N0  
          3rd Parm :     0      0   V2N5   V2N4   V2N3   V2N2   V2N1   V2N0  
          4th Parm :     0      0      0   V4N4   V4N3   V4N2   V4N1   V4N0  
          5th Parm :     0      0      0   V6N4   V6N3   V6N2   V6N1   V6N0  
          6th Parm :     0      0   J0N1   J0N0  V13N3  V13N2  V13N1  V13N0  
          7th Parm :     0  V20N6  V20N5  V20N4  V20N3  V20N2  V20N1  V20N0  
          8th Parm :     0  V36N2  V36N1  V36N0      0  V27N2  V27N1  V27N0  
          9th Parm :     0  V43N6  V43N5  V43N4  V43N3  V43N2  V43N1  V43N0  
         10th Parm :     0      0   J1N1   J1N0  V50N3  V50N2  V50N1  V50N0  
         11th Parm :     0      0      0  V57N4  V57N3  V57N2  V57N1  V57N0  
         12th Parm :     0      0      0  V59N4  V59N3  V59N2  V59N1  V59N0  
         13th Parm :     0      0  V61N5  V61N4  V61N3  V61N2  V61N1  V61N0  
         14th Parm :     0      0  V62N5  V62N4  V62N3  V62N2  V62N1  V62N0  

         Default Values
          VN0[3:0] : 0x00 
          VN1[5:0] : 0x2C 
          VN2[5:0] : 0x2E 
          VN4[4:0] : 0x15 
          VN6[4:0] : 0x10 
         VN13[3:0] : 0x09 
         VN20[6:0] : 0x48 
         VN27[2:0] : 0x03 
         VN36[2:0] : 0x03 
         VN43[6:0] : 0x53 
         VN50[3:0] : 0x0B 
         VN57[4:0] : 0x19 
         VN59[4:0] : 0x18 
         VN61[5:0] : 0x20 
         VN62[5:0] : 0x25
#############################################################################

DGMLUTR   0xE2 : Digital Gamma Look-up Table for Red
                 System Function Command Table 2.

          Parameter Descriptions 
           1st Parm : DGM_LUT_R00[7:0]  
           2nd Parm : DGM_LUT_R01[7:0]  
                  .....
          31th Parm : DGM_LUT_R30[7:0]  
          32th Parm : DGM_LUT_R31[7:0]  
                  .....
          63th Parm : DGM_LUT_R62[7:0]  
          64th Parm : DGM_LUT_R63[7:0]
            
          Default Values ( = RegNum * 4 )
          DGM_LUT_R00[7:0] 0x00 
          DGM_LUT_R01[7:0] 0x04 
                  .....
          DGM_LUT_R30[7:0] 0x78 
          DGM_LUT_R31[7:0] 0x7C 
                 .....
          DGM_LUT_R62[7:0] 0xF8 
          DGM_LUT_R63[7:0] 0xFC
#############################################################################
  
DGMLUTB   0xE3 : Digital Gamma Look-up Table for Blue
                 System Function Command Table 2.

          Parameter Descriptions 
           1st Parm : DGM_LUT_B00[7:0]  
           2nd Parm : DGM_LUT_B01[7:0]  
                  .....
          31th Parm : DGM_LUT_B30[7:0]  
          32th Parm : DGM_LUT_B31[7:0]  
                  .....
          63th Parm : DGM_LUT_B62[7:0]  
          64th Parm : DGM_LUT_B63[7:0]
          
          Default Values ( = RegNum * 4 ) 
          DGM_LUT_B00[7:0] 0x00 
          DGM_LUT_B01[7:0] 0x04 
                  .....
          DGM_LUT_B30[7:0] 0x78 
          DGM_LUT_B31[7:0] 0x7C 
                 .....
          DGM_LUT_B62[7:0] 0xF8 
          DGM_LUT_B63[7:0] 0xFC
#############################################################################

CMD2EN    0xDF : CMD2EN - Command 2 Enable (System Function Command)
                 System Function Command Table 2.
                 Cmds in cmd table 2 cannot be executed when EXTC is Low.
                 EXTC Pin Lo: system cmd 1 enabled, system cmd 2 disabled.
                 EXTC Pin Hi: system cmd 1 and 2 both enabled.
                 When programming NVM, this pin should connect to high level.  
 
          Parameter Descriptions 
          1st Parm :  0x5A 
          2nd Parm :  0x69 
          3nd Parm :  0x02 
          4nd Parm :  0x00 Disable, 0x01 = Enable
#############################################################################

