-- cpu.vhd: Simple 8-bit CPU (BrainLove interpreter)
-- Copyright (C) 2016 Brno University of Technology,
--                    Faculty of Information Technology
-- Author(s): Ivan Eštvan, xestva00
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

-- ----------------------------------------------------------------------------
--                        Entity declaration
-- ----------------------------------------------------------------------------
entity cpu is
 port (
   CLK   : in std_logic;  -- hodinovy signal
   RESET : in std_logic;  -- asynchronni reset procesoru
   EN    : in std_logic;  -- povoleni cinnosti procesoru
 
   -- synchronni pamet ROM
   CODE_ADDR : out std_logic_vector(11 downto 0); -- adresa do pameti
   CODE_DATA : in std_logic_vector(7 downto 0);   -- CODE_DATA <- rom[CODE_ADDR] pokud CODE_EN='1'
   CODE_EN   : out std_logic;                     -- povoleni cinnosti
   
   -- synchronni pamet RAM
   DATA_ADDR  : out std_logic_vector(9 downto 0); -- adresa do pameti
   DATA_WDATA : out std_logic_vector(7 downto 0); -- mem[DATA_ADDR] <- DATA_WDATA pokud DATA_EN='1'
   DATA_RDATA : in std_logic_vector(7 downto 0);  -- DATA_RDATA <- ram[DATA_ADDR] pokud DATA_EN='1'
   DATA_RDWR  : out std_logic;                    -- cteni (1) / zapis (0)
   DATA_EN    : out std_logic;                    -- povoleni cinnosti
   
   -- vstupni port
   IN_DATA   : in std_logic_vector(7 downto 0);   -- IN_DATA <- stav klavesnice pokud IN_VLD='1' a IN_REQ='1'
   IN_VLD    : in std_logic;                      -- data platna
   IN_REQ    : out std_logic;                     -- pozadavek na vstup data
   
   -- vystupni port
   OUT_DATA : out  std_logic_vector(7 downto 0);  -- zapisovana data
   OUT_BUSY : in std_logic;                       -- LCD je zaneprazdnen (1), nelze zapisovat
   OUT_WE   : out std_logic                       -- LCD <- OUT_DATA pokud OUT_WE='1' a OUT_BUSY='0'
 );
end cpu;


-- ----------------------------------------------------------------------------
--                      Architecture declaration
-- ----------------------------------------------------------------------------
architecture behavioral of cpu is

 -- zde dopiste potrebne deklarace signalu
	-- PC
	signal PC_reg:	std_logic_vector(11 downto 0);	-- ukazatel do ROM
	signal PC_inc: 	std_logic;			-- signal pre +1
	signal PC_dec: 	std_logic;			-- sinal pre -1

	-- PTR
	signal PTR_reg: std_logic_vector(9 downto 0); 	-- ukazatel do RAM
	signal PTR_inc: std_logic;			-- signal pre +1
	signal PTR_dec: std_logic;			-- signal pre -1

	-- CNT
	signal CNT_reg: std_logic_vector(6 downto 0);	-- 0000 - 4 bit counter
	signal CNT_inc: std_logic;
	signal CNT_dec: std_logic;
	
	-- TMP
	signal TMP_reg: std_logic_vector(7 downto 0);
	signal TMP_ld: std_logic;

	-- MX
	signal MX_sel: std_logic_vector(1 downto 0);
	
	-- INSTRUCTION
	type INST_type is (inc_pointer, dec_pointer, inc_val, dec_val, start_while, end_while, print_val, load_val, save_tmp, tmp_val, end_prog, nthing);
	signal INST_dec: INST_type;


	-- FSM - radic
	type FSM_state is (sInit,sFetch, sFetch_delay, sDecode, sInc_pointer,sDec_pointer,sInc_val,sDec_val,sStart_while,sEnd_while,sPrint_val,sLoad_val,sSave_tmp,sTmp_val,sEnd_prog,sNthing,sInc_val_next,
	sDec_val_next, sPrint_val_next,sLoad_val_next,sSave_tmp_next,sStart_while_if,sStart_while_while,sStart_while_if2,
	sEnd_while_if,sEnd_while_while,sEnd_while_if2, sInc_val_delay, sDec_val_delay, sPrint_val_delay);
	signal pres_state: FSM_state;
	signal next_state: FSM_state;


begin

 -- zde dopiste vlastni VHDL kod
	-- PC process
	PC_proc: process (RESET, CLK)
	begin
		if (RESET='1') then
			PC_reg <= (others=>'0');
		elsif (CLK'event) and (CLK='1') then
			if (PC_inc='1') then
				PC_reg<= PC_reg + 1;
			elsif (PC_dec='1') then
				PC_reg<= PC_reg - 1;
			end if;
		end if;
	end process;
	
	CODE_ADDR <= PC_reg;

	-- PTR process
	PTR_proc: process (RESET, CLK)
	begin
		if (RESET='1') then
			PTR_reg <= (others=>'0');
		elsif (CLK'event) and (CLK='1') then
			if (PTR_inc='1') then
				PTR_reg<=PTR_reg + 1;	
			elsif (PTR_dec='1') then
				PTR_reg<=PTR_reg - 1;
			end if;
		end if;
	end process;
	
	DATA_ADDR <= PTR_reg;
	
	-- CNT process
	CNT_proc: process (RESET, CLK)
	begin
		if (RESET='1') then
			CNT_reg<= (others=>'0');
		elsif (CLK'event) and (CLK='1') then
			if (CNT_inc='1') then
				CNT_reg<=CNT_reg + 1;
			elsif (CNT_dec='1') then
				CNT_reg<=CNT_reg - 1;
			end if;
		end if;
	end process;

	-- TMP process
	TMP_proc: process (RESET, CLK)
	begin
		if (RESET='1') then
			TMP_reg<= (others=>'0');
		elsif (CLK'event) and (CLK='1') then
			if (TMP_ld='1') then
				TMP_reg<=DATA_RDATA;	
			end if;
		end if;
	end process;

	-- MX 
	with MX_sel select
	DATA_WDATA<=IN_DATA when "00",
	DATA_RDATA + "00000001" when "01",
	DATA_RDATA - "00000001" when "10",
	TMP_reg when "11",
	"00000000" when others;

	-- INSTRUCTION DECODER
	DECODER_proc: process(CODE_DATA)
	begin
		case CODE_DATA is
			when X"3E" => INST_dec <= inc_pointer;
			when X"3C" => INST_dec <= dec_pointer;
			when X"2B" => INST_dec <= inc_val;
			when X"2D" => INST_dec <= dec_val;
			when X"5B" => INST_dec <= start_while;
			when X"5D" => INST_dec <= end_while;
			when X"2E" => INST_dec <= print_val;
			when X"2C" => INST_dec <= load_val;
			when X"24" => INST_dec <= save_tmp;
			when X"21" => INST_dec <= tmp_val;
			when X"00" => INST_dec <= end_prog;
			when others => INST_dec <= nthing;
		end case;
	end process;

	--FSM Present Proces
	FSM_pres_proc: process (RESET, CLK)
	begin
		if (RESET='1') then
			pres_state <= sInit; --init
		elsif (CLK'event) and (CLK='1') then
			if (EN='1') then
				pres_state<= next_state;
			end if;
		end if;
	end process;

	-- FSM Next Proces
	FSM_next_proc: process(pres_state, PC_inc, PC_dec, PTR_inc, PTR_dec, CNT_inc,CNT_dec,
	TMP_ld,INST_dec,next_state,PC_reg,PTR_reg,CNT_reg,TMP_reg,MX_sel, OUT_BUSY, DATA_RDATA, IN_VLD)
	begin
	
	-- Inicializacia

	PC_inc <= '0';
	PC_dec <= '0';
	PTR_inc <= '0';
	PTR_dec <= '0';
	CNT_inc <= '0';
	CNT_dec <= '0';
	TMP_ld <= '0';
	MX_sel <= "11";
	CODE_EN <= '0';
	DATA_EN <= '0';
	OUT_WE <= '0';
	DATA_RDWR <= '1';
	IN_REQ <= '0';
	

	case (pres_state) is
		when sInit => next_state <= sFetch;
		-- Instruction fetch
		when sFetch =>
			next_state <= sFetch_delay;
			CODE_EN <= '1';
		when sFetch_delay => next_state <= sDecode;
		when sDecode =>
			case (INST_dec) is
				when inc_pointer => next_state <= sInc_pointer;
				when dec_pointer => next_state <= sDec_pointer;
				when inc_val => next_state <= sInc_val;
				when dec_val => next_state <= sDec_val;
				when start_while => next_state <= sStart_while;
				when end_while => next_state <= sEnd_while;
				when print_val => next_state <= sPrint_val;
				when load_val => next_state <= sLoad_val;
				when save_tmp => next_state <= sSave_tmp;
				when tmp_val => next_state <= sTmp_val;
				when end_prog => next_state <= sEnd_prog;
				when nthing => next_state <= sNthing;	
			end case;
		when sNthing =>
			PC_inc <= '1';
			next_state <= sFetch;
		when sEnd_prog => next_state <= sEnd_prog;
		when sInc_pointer =>
			PC_inc <= '1';
			PTR_inc <= '1';
			next_state <= sFetch;
		when sDec_pointer =>
			PC_inc <= '1';
			PTR_dec <= '1';
			next_state <= sFetch;
		-- Mozno bude treba opravit najprv nacitat atd.
		when sInc_val =>
			PC_inc <= '1';
			DATA_EN <= '1';
			DATA_RDWR <= '1'; -- nacitanie
			--MX_sel <= "01";
			next_state <= sInc_val_delay;
		when sInc_val_delay =>
			DATA_EN <= '1';
			DATA_RDWR <= '1'; -- nacitanie
			--MX_sel <= "01";
			next_state <= sInc_val_next;
		when sInc_val_next =>
			MX_sel <= "01";
			DATA_EN <= '1';
			DATA_RDWR <= '0'; -- zapis
			next_state <= sFetch;

		when sDec_val =>
			PC_inc <= '1';
			DATA_EN <= '1';	
			DATA_RDWR <= '1'; --nacitanie
			--MX_sel <= "10";
			next_state <= sDec_val_delay;
		when sDec_val_delay =>
			DATA_EN <= '1';	
			DATA_RDWR <= '1'; --nacitanie
			--MX_sel <= "10";
			next_state <= sDec_val_next;
		when sDec_val_next =>
			MX_sel <= "10";
			DATA_EN <= '1';
			DATA_RDWR <= '0'; --zapis

			next_state <= sFetch;

		-- Print val
		when sPrint_val =>
			PC_inc <= '1';
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			next_state <= sPrint_val_delay;
		when sPrint_val_delay =>
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			next_state <= sPrint_val_next;
		when sPrint_val_next =>
			if (OUT_BUSY = '0') then
				OUT_DATA <= DATA_RDATA;
				OUT_WE <= '1';
				next_state <= sFetch;
			else
				next_state <= sPrint_val_next;
			end if;
		-- zapis vstupu z klavesnice		
		when sLoad_val =>
			PC_inc <= '1';
			IN_REQ <= '1';
			next_state <= sLoad_val_next;
		when sLoad_val_next =>
			IN_REQ <= '1';
			if(IN_VLD = '1') then
				MX_sel <= "00";
				DATA_EN <='1';
				DATA_RDWR <= '0';

				next_state <= sFetch;
			else
				next_state <= sLoad_val_next;
			end if;
		
		when sSave_tmp =>
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			PC_inc <= '1';
			next_state <= sSave_tmp_next;
		when sSave_tmp_next =>
			TMP_ld <= '1';
			next_state <= sFetch;

		when sTmp_val =>
			PC_inc <= '1';
			DATA_EN <= '1';
			DATA_RDWR <= '0';
			MX_sel <= "11";
			next_state <= sFetch;
			
		when sStart_while =>		
			PC_inc <= '1';
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			next_state <= sStart_while_if;
		when sStart_while_if =>
			if (DATA_RDATA = "00000000") then
				CNT_inc <= '1';
				next_state <= sStart_while_while;
				--next_state <= sFetch;
			else
				--CNT_inc <= '1'; -- CNT <- 1
				--next_state <= sStart_while_while;
				next_state <= sFetch;
			end if;
		when sStart_while_while =>
			if (CNT_reg = "0000000") then
				--CNT_inc <= '1'; -- CNT <- 1
				next_state <= sFetch;
			else
				CODE_EN <= '1';
				next_state <= sStart_while_if2;
			end if;
		when sStart_while_if2 =>
			if ( INST_dec = start_while) then
				CNT_inc <= '1';
			elsif ( INST_dec = end_while) then
				CNT_dec <= '1';
			end if;
			PC_inc <= '1';
			next_state <= sStart_while_while;

		when sEnd_while =>
			DATA_EN <= '1';
			DATA_RDWR <= '1';
			next_state <= sEnd_while_if;
		when sEnd_while_if =>
			if (DATA_RDATA = "00000000") then
				PC_inc <= '1';
				next_state <= sFetch;
			else
				CNT_inc <= '1';
				PC_dec <= '1';
				next_state <= sEnd_while_while;
			end if;
		when sEnd_while_while =>
			if (CNT_reg = "0000000") then 
				PC_inc <= '1';
				next_state <= sFetch;
			else 
				CODE_EN <= '1';
				next_state <= sEnd_while_if2;
			end if;
		when sEnd_while_if2 =>
			if (INST_dec = end_while) then
				CNT_inc <= '1';
			elsif (INST_dec = start_while) then
				CNT_dec <= '1';
			end if;
			if(CNT_reg = "0000000") then
				PC_inc <= '1';
			else 
				PC_dec <= '1';
			end if;
			next_state <= sEnd_while_while;

		when others => null;
	end case;
	end process;

end behavioral;
 
