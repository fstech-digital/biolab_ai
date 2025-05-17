"use client";

import { ReactNode } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

import { useSession } from "next-auth/react";

interface AppLayoutProps {
  children: ReactNode;
  breadcrumb?: {
    parent?: { label: string; href: string };
    current: string;
  };
}

export default function AppLayout({ children, breadcrumb }: AppLayoutProps) {
  const { data: session } = useSession();
  const role = session?.user?.role ?? "user";

  return (
    <SidebarProvider>
      <AppSidebar role={role} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 text-white">
          <div className="flex items-center gap-2 px-4 ">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-8" />
            <Breadcrumb>
              <BreadcrumbList>
                {breadcrumb?.parent && (
                  <>
                    <BreadcrumbItem className="hidden md:block ">
                      <BreadcrumbLink href={breadcrumb.parent.href}>
                        {breadcrumb.parent.label}
                      </BreadcrumbLink>
                    </BreadcrumbItem>
                    <BreadcrumbSeparator className="hidden md:block" />
                  </>
                )}
                <BreadcrumbItem>
                  <BreadcrumbPage className="text-white text-xl">
                    {breadcrumb?.current}
                  </BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
