export type MachineStatus = "Normal" | "Warning" | "Critical";

export type Machine = {
  id: string;
  name: string;
  type: string;
  line: string;
  score: number;
  status: MachineStatus;
  maintenance: string;
  reading: string;
};

export const machines: Machine[] = [
  { id: "induction-furnace-01", name: "Induction Furnace 01", type: "Melting furnace", line: "Foundry Line A", score: 92, status: "Normal", maintenance: "18 Aug 2024", reading: "182 kW" },
  { id: "compressor-02", name: "Air Compressor 02", type: "Rotary screw compressor", line: "Utilities", score: 76, status: "Warning", maintenance: "04 Jul 2024", reading: "68 kW" },
  { id: "cnc-lathe-04", name: "CNC Lathe 04", type: "CNC turning centre", line: "Machining Line B", score: 88, status: "Normal", maintenance: "22 Aug 2024", reading: "41 kW" },
  { id: "dust-collector-01", name: "Dust Collector 01", type: "Baghouse filter", line: "Foundry Line A", score: 61, status: "Critical", maintenance: "12 Jun 2024", reading: "29 kW" },
  { id: "cooling-tower-01", name: "Cooling Tower 01", type: "Induced draft", line: "Utilities", score: 84, status: "Normal", maintenance: "30 Jul 2024", reading: "36 kW" },
];

export const energyTrend = [46, 58, 52, 68, 61, 76, 69, 81, 73, 86, 78, 92, 84, 98, 89, 104, 96, 110, 100, 115, 108, 123, 112, 118];
export const detailTrend = [62, 68, 64, 75, 72, 80, 78, 86, 83, 90, 87, 94, 92, 98, 96, 102, 99, 106, 103, 111, 108, 114, 111, 116];

export const alerts = [
  { id: 1, title: "Dust Collector 01 · High vibration", detail: "Vibration has exceeded the safe threshold for 18 minutes.", time: "12 min ago", severity: "Critical", machine: "Dust Collector 01" },
  { id: 2, title: "Air Compressor 02 · Efficiency drop", detail: "Power draw is 14% above its normal operating baseline.", time: "38 min ago", severity: "Warning", machine: "Air Compressor 02" },
  { id: 3, title: "Induction Furnace 01 · Temperature stable", detail: "Operating temperature returned to the expected range.", time: "2 hrs ago", severity: "Resolved", machine: "Induction Furnace 01" },
  { id: 4, title: "CNC Lathe 04 · Maintenance due soon", detail: "Preventive service is recommended within the next 12 days.", time: "Yesterday", severity: "Info", machine: "CNC Lathe 04" },
];

export const recommendations = [
  { rank: "01", title: "Repair compressed-air leak on Line 2", description: "Fix the flagged leak near the pneumatic manifold to reduce compressor runtime.", saving: "1,240 kWh", rupees: "₹10,540 / mo", payback: "0.8 months", tag: "Quick win" },
  { rank: "02", title: "Install VFD on cooling tower fan", description: "Match fan speed to cooling demand during partial-load production hours.", saving: "2,860 kWh", rupees: "₹24,310 / mo", payback: "4.2 months", tag: "High impact" },
  { rank: "03", title: "Replace furnace door seals", description: "Reduce heat loss and stabilize the induction furnace warm-up cycle.", saving: "1,980 kWh", rupees: "₹16,830 / mo", payback: "6.1 months", tag: "Maintenance" },
  { rank: "04", title: "Shift batch pre-heating to off-peak hours", description: "Move the pre-heating window to lower-tariff periods without changing output.", saving: "—", rupees: "₹8,400 / mo", payback: "Immediate", tag: "No capex" },
];
