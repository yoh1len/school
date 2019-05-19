-- Meno: Ivan Estvan
-- login: xestva00
-- last edit: 27.10.2016 23:41


library IEEE;
use IEEE.std_logic_arith.all;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_unsigned.all;

entity ledc8x8 is
	port(
		SMCLK: in std_logic;
		ROW: out std_logic_vector (0 to 7);
		LED: out std_logic_vector (0 to 7);
		RESET: in std_logic		
	);
end entity ledc8x8;

architecture mat_display of ledc8x8 is
	signal delay: STD_LOGIC_VECTOR (21 downto 0);
	signal sig_counter: STD_LOGIC_VECTOR (7 downto 0);
	signal rows: STD_LOGIC_VECTOR (7 downto 0) := "00000001";
	signal leds: STD_LOGIC_VECTOR (7 downto 0) := "00000000";
	signal enabled: STD_LOGIC;
	signal change: STD_LOGIC;
begin
signal_counter_p: process (RESET, SMCLK, enabled, sig_counter, delay)
begin
	if RESET = '1' then
		sig_counter <= "00000000";   
		change <= '1';
		delay <="0000000000000000000000";
	elsif SMCLK = '1' and SMCLK'event then
			sig_counter <= sig_counter + "1";
			delay <= delay + 1;
			if delay="1111111111111111111111" and change = '1' then
				change <= '0';
			elsif delay="1111111111111111111111" and change = '0' then
				change <= '1';
			end if;
		if sig_counter = "11111111" then
			enabled <= '1';
		else
			enabled <= '0';
		end if; 
	end if;
end process signal_counter_p;

rows_p: process (RESET, SMCLK, enabled, rows)
begin 
	if RESET= '1' then
		rows <= "00000001";
	elsif enabled = '1' and SMCLK = '1' and SMCLK'event then
	
				if rows = "00000001" then
					rows <= "10000000";
				
				elsif rows = "00000010" then
					rows <= "00000001";
				
				elsif rows = "00000100" then
					rows <= "00000010";
				
				elsif rows = "00001000" then
					rows <= "00000100";
				
				elsif rows = "00010000" then
					rows <= "00001000";
				
				elsif rows = "00100000" then
					rows <= "00010000";
				
				elsif rows = "01000000" then
					rows <= "00100000";
				
				elsif rows = "10000000" then
					rows <= "01000000";
				end if;
	end if;
end process rows_p;

led_p: process (SMCLK,rows,change)
begin
	  if change = '1'  then
	 	if SMCLK = '1' and SMCLK'event then
		
				if rows = "10000000" then
					leds <= "11111111";
					
				elsif rows = "01000000" then
					leds <= "10111111";
					
				elsif rows = "00100000" then
					leds <= "10111111";
					
				elsif rows = "00010000" then
					leds <= "10111111";
					
				elsif rows = "00001000" then
					leds <= "10111111";
					
				elsif rows = "00000100" then
					leds <= "10111111";
					
				elsif rows = "00000010" then
					leds <= "11111111";
					
				elsif rows = "00000001" then
					leds <= "11111111";
				end if;

		ROW <= rows;
		LED <= leds;
		end if;
	elsif change = '0' then
		if SMCLK = '1' and SMCLK'event then
		
				if rows = "10000000" then
					leds <= "11111111";
					
				elsif rows = "01000000" then
					leds <= "11111111";
					
				elsif rows = "00100000" then
					leds <= "11111111";
					
				elsif rows = "00010000" then
					leds <= "11100001";
					
				elsif rows = "00001000" then
					leds <= "11101111";
					
				elsif rows = "00000100" then
					leds <= "11100011";
					
				elsif rows = "00000010" then
					leds <= "11101111";
					
				elsif rows = "00000001" then
					leds <= "11100001";
				end if;

		ROW <= rows;
		LED <= leds;
		end if;
	end if;
end process led_p;
end architecture mat_display;	
