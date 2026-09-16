import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";

export type Language = "en" | "hi";

interface TranslationDictionary {
  [key: string]: {
    en: string;
    hi: string;
  };
}

const translations: TranslationDictionary = {
  // Navigation
  "nav.dashboard": { en: "Dashboard", hi: "डैशबोर्ड" },
  "nav.machines": { en: "Machines", hi: "मशीनें" },
  "nav.alerts": { en: "Alerts", hi: "अलर्ट" },
  "nav.audit": { en: "Energy audit", hi: "ऊर्जा ऑडिट" },
  "nav.simulate": { en: "Simulator", hi: "सिम्युलेटर" },
  "nav.plant_settings": { en: "Plant settings", hi: "प्लांट सेटिंग्स" },
  "nav.help_center": { en: "Help center", hi: "सहायता केंद्र" },

  // Plant & Header
  "plant.name": { en: "Rajkot Foundry Unit", hi: "राजकोट फाउंड्री यूनिट" },
  "header.data_refreshed": { en: "Data refreshed 32s ago", hi: "डेटा 32 सेकंड पहले अपडेट हुआ" },
  "plant.live": { en: "Live", hi: "लाइव" },
  "plant.status": { en: "Plant status", hi: "प्लांट स्थिति" },

  // Dashboard Stats
  "stat.energy_use": { en: "Today’s energy use", hi: "आज की ऊर्जा खपत" },
  "stat.energy_cost": { en: "Today’s energy cost", hi: "आज की ऊर्जा लागत" },
  "stat.co2_emitted": { en: "CO₂e emitted", hi: "CO₂e उत्सर्जन" },
  "stat.active_alerts": { en: "Active alerts", hi: "सक्रिय अलर्ट" },
  "stat.health_score": { en: "Overall energy health", hi: "समग्र ऊर्जा स्वास्थ्य" },
  "stat.plant_score": { en: "Plant score", hi: "प्लांट स्कोर" },
  "stat.healthy_range": { en: "Healthy operating range", hi: "सुरक्षित ऑपरेटिंग रेंज" },
  "stat.vs_last_week": { en: "vs. last week", hi: "पिछले सप्ताह की तुलना" },

  // Dashboard sections
  "dash.load_title": { en: "Plant load over time", hi: "समय के साथ प्लांट लोड" },
  "dash.load_desc": { en: "Aggregate energy use across 5 monitored machines", hi: "5 निगरानी मशीनों में कुल ऊर्जा खपत" },
  "dash.attention_title": { en: "Latest alerts", hi: "नवीनतम अलर्ट" },
  "dash.view_all_alerts": { en: "View all alerts", hi: "सभी अलर्ट देखें" },
  "dash.benchmark_title": { en: "Peer Benchmarking", hi: "सहकर्मी बेंचमार्किंग" },

  // Machines
  "machines.title": { en: "Machines", hi: "मशीनें" },
  "machines.desc": { en: "A clear view of health, operating status, and service readiness across the plant.", hi: "प्लांट में स्वास्थ्य, ऑपरेटिंग स्थिति और सेवा तत्परता का स्पष्ट विवरण।" },
  "machines.search": { en: "Search machines", hi: "मशीनें खोजें..." },
  "machines.all": { en: "All machines", hi: "सभी मशीनें" },
  "machines.attention": { en: "Needs attention", hi: "ध्यान देने योग्य" },
  "machines.healthy": { en: "Healthy", hi: "स्वस्थ" },
  "machines.live_telemetry": { en: "Live telemetry", hi: "लाइव टेलीमेट्री" },
  "machines.power_draw": { en: "Power draw", hi: "पावर खपत" },
  "machines.temperature": { en: "Temperature", hi: "तापमान" },
  "machines.vibration": { en: "Vibration", hi: "कंपन" },

  // Alerts
  "alerts.title": { en: "Alerts", hi: "अलर्ट" },
  "alerts.desc": { en: "Stay ahead of issues with machine events ordered by urgency.", hi: "प्राथमिकता के अनुसार व्यवस्थित मशीन घटनाओं की जानकारी रखें।" },
  "alerts.whatsapp_toggle": { en: "Send critical alerts to WhatsApp", hi: "महत्वपूर्ण अलर्ट व्हाट्सएप पर भेजें" },

  // Audit & Simulator
  "audit.title": { en: "Energy audit", hi: "ऊर्जा ऑडिट" },
  "audit.desc": { en: "Turn your plant’s energy signals into a ranked action plan with clear financial impact.", hi: "अपने प्लांट के ऊर्जा संकेतों को स्पष्ट वित्तीय लाभ वाली कार्य योजना में बदलें।" },
  "audit.schemes_title": { en: "BEE & Government Energy Schemes", hi: "BEE एवं सरकारी ऊर्जा योजनाएं" },
  "sim.title": { en: "What-If Simulator", hi: "व्हाट-इफ सिम्युलेटर" },
  "sim.desc": { en: "Model the financial & energy impact of load shifting, VFD retrofits, and leak fixes before investing.", hi: "निवेश से पहले लोड शिफ्टिंग, VFD रेट्रोफिट और लीक सुधार के वित्तीय प्रभाव का आकलन करें।" },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, defaultText?: string) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  language: "en",
  setLanguage: () => {},
  t: (key: string, defaultText?: string) => defaultText || key,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("enersense_lang") as Language;
      if (stored === "en" || stored === "hi") return stored;
    }
    return "en";
  });

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("enersense_lang", language);
    }
  }, [language]);

  const t = (key: string, defaultText?: string): string => {
    const entry = translations[key];
    if (entry && entry[language]) {
      return entry[language];
    }
    return defaultText || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useTranslation() {
  return useContext(LanguageContext);
}
