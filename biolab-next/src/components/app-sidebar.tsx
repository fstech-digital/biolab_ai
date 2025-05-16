"use client";

import * as React from "react";
import {
  BookOpen,
  Bot,
  Command,
  Frame,
  LifeBuoy,
  Map,
  PieChart,
  Send,
  Settings2,
  SquareTerminal,
} from "lucide-react";

import Image from "next/image";

import { NavMain } from "@/components/nav-main";
import { NavProjects } from "@/components/nav-projects";
import { NavSecondary } from "@/components/nav-secondary";
import { NavUser } from "@/components/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

import { useSession } from "next-auth/react";

const commonNavMain = [
  {
    title: "Playground",
    url: "#",
    icon: SquareTerminal,
    isActive: true,
    items: [
      { title: "History", url: "#" },
      { title: "Starred", url: "#" },
      { title: "Settings", url: "#" },
    ],
  },
  {
    title: "Models",
    url: "#",
    icon: Bot,
    items: [
      { title: "Genesis", url: "#" },
      { title: "Explorer", url: "#" },
      { title: "Quantum", url: "#" },
    ],
  },
];

const adminNavMain = [
  {
    title: "Administração",
    url: "/admin",
    icon: Settings2,
    items: [
      { title: "Usuários", url: "#" },
      { title: "Configurações", url: "#" },
    ],
  },
];

const navSecondary = [
  {
    title: "Suporte",
    url: "#",
    icon: LifeBuoy,
  },
  {
    title: "Feedback",
    url: "#",
    icon: Send,
  },
];

const navProjects = [
  {
    name: "Design e Engenharia",
    url: "#",
    icon: Frame,
  },
  {
    name: "Vendas e Marketing",
    url: "#",
    icon: PieChart,
  },
  {
    name: "Viagens",
    url: "#",
    icon: Map,
  },
];

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  role?: "admin" | "user";
}

export function AppSidebar({ role = "user", ...props }: AppSidebarProps) {
  const navMain =
    role === "admin" ? [...commonNavMain, ...adminNavMain] : commonNavMain;

  const { data: session } = useSession();

  const user = session?.user;

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/" className="flex items-center gap-3">
                <Image
                  src="/Icon.png"
                  alt="BioLab Logo"
                  width={48}
                  height={48}
                  className="rounded-md"
                />
                <div className="grid text-left text-sm leading-tight">
                  <span className="truncate font-semibold text-sidebar-foreground">
                    BioLab
                  </span>
                  <span className="truncate text-xs text-muted-foreground">
                    Inteligência Clínica
                  </span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
        <NavProjects projects={navProjects} />
        <NavSecondary items={navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser
          user={{
            name: user?.name || "Usuário",
            email: user?.email || "",
            avatar: user?.image || "",
          }}
        />
      </SidebarFooter>
    </Sidebar>
  );
}
